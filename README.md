# Pipeline Analyzer

Pipeline analyzer includes a portable DSL parser based on `pyparsing` and a figure drawer based on `matplotlib`.

## Install the Highlighter Extension for VSCode

In the following tutorial, we use `Command("command")` to represent searching and running the command `<command>` in VSCode Command Palette. Usually, you can open the palette by shotcut keys `Shift + Command + P` in MacOS and `Ctrl + Shift + P` in Windows/Linux.
1. Clone or download this repository.
2. Command("Extensions: Open Extensions Folder") -> Copy the directry `pipeline.vscode` to the extensions folder -> Command("Developer: Reload Window")
3. Command("Preferences: Open User Settings (JSON)") -> Copy JSON settings in `pipeline.vscode/settings.json` (starting from Line 2) and insert them into the VSCode's user settings.

## Example of Usage

We provide an example of usage in `example.py` with dependency definitions in `example.ppl`/`example_h.ppl` and output figure `example.png`.

```python
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
    'ThereD': '#E2F0D9', 'HereD': '#FFF2CC',
    'ThereT': '#DAE3F3', 'HereT': '#DAE3F3',
    'here': '#FFF8E5', 'there': '#F0F7EB'
} 
figure = DiagramDrawer(
    max_ylim=11, ylabel="sequence"
    ).draw(tasks, events, period, groups, colors)
figure.savefig('example.png')
```

![](./example.png)