import re
from pyparsing import (
    alphas, alphanums, nums,
    Word, Keyword, Literal, Suppress, OneOrMore, 
    restOfLine, ParserElement, QuotedString, Optional
)

ParserElement.setDefaultWhitespaceChars(" \t\n")

class Task:
    
    duration: float = 0
    group: str = ""

    def __init__(self, name, label):
        self.name = name
        self.class_name = self.__class__.__name__
        self.label = label
        self.idx = int(re.compile(r"\d+").search(name).group())
        self.start_time = 0
        self.finish_time = 0
    
    def __repr__(self):
        return f"{self.class_name}" \
            f"({self.name}, {self.start_time:>4.1f}, {self.finish_time:>4.1f})"

class Event:

    def __init__(self, name, task, when, label):
        self.name = name
        self.task = task
        self.time = None
        self.when = when
        self.label = label

    def compute_time(self):
        if self.when == 'start':
            self.time = self.task.start_time 
        else:
            self.time = self.task.finish_time

class Period:

    def __init__(self, start: Event, finish: Event, label):
        self.start = start
        self.finish = finish
        self.start_time = None
        self.finish_time = None
        self.label = label

    def compute_time(self):
        self.start_time = self.start.time
        self.finish_time = self.finish.time

class Pipeline:
    def __init__(self):
        self.classes = {}
        self.objects = {}
        self.dependencies = {}
        self.events = {}
        self.period = None
    
    def arange_tasks(self):
        deps = self.dependencies.copy()
        tasks = set()
        while True:
            current_task = None
            for task in deps:
                if not deps[task] or all(dep not in deps for dep in deps[task]):
                    current_task = task
                    break
            if current_task is None:
                break
            self.objects[current_task].start_time = max([self.objects[dep].finish_time for dep in deps[current_task]], default=0)
            self.objects[current_task].finish_time = self.objects[current_task].start_time + self.objects[current_task].duration
            del deps[current_task]
            tasks.add(self.objects[current_task])
        return tasks
    
    def compute_events(self):
        events = list(self.events.values())
        for event in events:
            event.compute_time()
        return events
    
    def compute_period(self):
        if self.period is not None:
            self.period.compute_time()
        return self.period

class PipelineParser:

    _keywords = {
        "declare":  Keyword("task"),
        "duration": Keyword("duration"),
        "group":    Keyword("group"),
        "after":    Keyword("after"),
        "range":    Keyword("range"),
        "null":     Keyword("null"),
        "label":    Keyword("label"),
        "event":    Keyword("event"),
        "at":       Keyword("at"),
        "finish":   Keyword("finish"),
        "start":    Keyword("start"),
        "period":   Keyword("period"),
        "to":       Keyword("to"),
    }
    _tokens = {
        "task_cls": Word(alphas + "_"),
        "task_obj": Word(alphas + "_"),
        "task_ref": Word(alphanums + "_"),
        "duration": Word(nums + "."),
        "group":    QuotedString('"'),
        "range":    Word(nums) + Suppress("-") + Word(nums),
        "label":    QuotedString('"'),
        "event":    Word(alphanums + "_"),
    }

    def _task_declaration(self):
        def to_dict(tokens):
            return {tokens[i]: tokens[i + 1] for i in range(0, len(tokens), 2)}

        def declare(tokens):
            _, class_name, attributes = tokens
            self.pipeline.classes[class_name] = type(class_name, (Task, ), attributes)

        attributes = OneOrMore(
            (self._keywords['duration'] + Suppress(":") + self._tokens['duration'].setParseAction(lambda t: float(t[0]))) + Suppress(";")
            | (self._keywords['group'] + Suppress(":") + self._tokens['group']) + Suppress(";")
        ).setParseAction(to_dict)
        task_declaration = (
            self._keywords['declare'] + self._tokens['task_cls'] + Suppress("{") + attributes + Suppress("}") + Suppress(";")
        ).setParseAction(declare)

        return task_declaration
    
    def _task_definition(self):
        def define(tokens):
            class_name, obj_name, _, beg, end, *label = tokens
            for i in range(int(beg), int(end) + 1):
                task_name = f"{obj_name}{i}"
                task_label = label[1] if label else ""
                task = self.pipeline.classes[class_name](task_name, task_label)
                self.pipeline.objects[task_name] = task

        task_definition = (
            self._tokens["task_cls"] + self._tokens["task_obj"] + 
            self._keywords["range"] + self._tokens["range"] + 
            Optional(self._keywords["label"] + self._tokens["label"]) +
            Suppress(";")
        ).setParseAction(define)
        
        return task_definition
    
    def _dependency(self):
        def build_dependency(tokens):
            task, _, *dependencies = tokens
            if 'null' in dependencies:
                dependencies.remove('null')
            self.pipeline.dependencies[task] = list(set(dependencies))

        dependency = (
            self._tokens["task_ref"] + self._keywords["after"] + 
            (self._keywords['null'] | OneOrMore(self._tokens["task_ref"])) + Suppress(";")
        ).setParseAction(build_dependency)
        return dependency
    
    def _event(self):
        def build_event(tokens):
            _, event_name, _, task_name, when, *label = tokens
            task = self.pipeline.objects[task_name]
            event_label = label[1] if label else ""
            self.pipeline.events[event_name] = Event(event_name, task, when, event_label)

        event = (
            self._keywords["event"] + self._tokens["event"] + 
            self._keywords["at"] + self._tokens["task_ref"] + 
            (self._keywords['start'] | self._keywords['finish']) + 
            Optional(self._keywords['label'] + self._tokens['label']) +
            Suppress(";")
        ).setParseAction(build_event)
        return event

    def _period(self):
        def build_period(tokens):
            _, start_event, _, finish_event, *label = tokens
            period_label = label[1] if label else ""
            start_event = self.pipeline.events[start_event]
            finish_event = self.pipeline.events[finish_event]
            self.pipeline.period = Period(start_event, finish_event, period_label)

        period = (
            self._keywords["period"] + self._tokens["event"] + self._keywords['to'] + self._tokens["event"] + 
            Optional(self._keywords['label'] + self._tokens['label']) +
            Suppress(";")
        ).setParseAction(build_period)
        return period
    
    def _comment(self):
        comment = Literal("//") + restOfLine
        return comment

    def __init__(self):
        self.pipeline: Pipeline = None
        self.parser = OneOrMore(
            self._task_declaration()
            | self._task_definition() 
            | self._dependency() 
            | self._event()
            | self._period()
            | self._comment()
        )
    
    def keywords(self):
        return self._keywords.keys()
    
    def parse_string(self, string):
        self.pipeline = Pipeline()
        self.parser.parseString(string)
        return self.pipeline

    def parse_file(self, file_name):
        with open(file_name, "r") as istream:
            return self.parse_string(istream.read())