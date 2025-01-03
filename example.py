from pipeline_parser import PipelineParser
from pipeline_drawer import DiagramDrawer

parser = PipelineParser()
parsed = parser.parse_file("example.ppl")

tasks = parsed.arange_tasks()
events = parsed.compute_events()
period = parsed.compute_period()
groups = {
    'here': 1, 'there': 0
}
colors = {
    'ThereD': '#E2F0D9',
    'HereD': '#FFF2CC',
    'ThereT': '#DAE3F3',
    'HereT': '#DAE3F3',
    'here': '#FFF8E5',
    'there': '#F0F7EB'
} 
figure = DiagramDrawer(max_ylim=11, ylabel="sequence").draw(tasks, events, period, groups, colors)
figure.savefig('example.png')
