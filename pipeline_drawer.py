from pipeline_parser import Task, Event, Period
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import ArrowStyle
from typing import List
import numpy as np


class DiagramDrawer:
    def __init__(self, **kwargs):
        self.zorder = 1
        self.config = {
            'font.size': 18,
            'dpi': 80,
            'ylabel': "",
            **kwargs
        }
    
    def _draw_task(self, task: Task, ax, color):
        ax.add_patch(patches.Rectangle(
            xy=(task.start_time, task.idx), width=task.duration, height=1, 
            edgecolor='black', facecolor=color, zorder=self.zorder))
        ax.text(
            x=task.start_time + task.duration / 2, y=task.idx + 0.5, s=task.label, 
            ha='center', va='center', color='black', fontsize=self.config['font.size'], 
            zorder=self.zorder + 1)
        self.zorder += 1
    
    def _draw_event(self, event: Event, axes):
        for ax in axes:
            ax.axvline(x=event.time, color='blue', linestyle='--', zorder=1)
        axes[0].text(
            x=event.time, y=0.5, s=event.label, 
            ha='center', va='center', color='blue', fontsize=self.config['font.size'], 
            zorder=1)
    
    def _draw_period(self, period: Period, axes):
        if period is None:
            return
        annote_y = 4
        arrowprops = {
            "color": "black", 
            "arrowstyle": ArrowStyle.CurveFilledAB(
                head_width=0.3, 
                head_length=1.5
            )
        }
        axes[0].annotate(
            text='', xy=(period.start_time, annote_y), xytext=(period.finish_time, annote_y), 
            arrowprops=arrowprops, zorder=self.zorder)
        self.zorder += 1
        axes[0].text(
            x=period.start_time + (period.finish_time - period.start_time) / 2, y=annote_y, 
            s=period.label, fontsize=self.config['font.size'],
            ha='center', va='center', color='black', zorder=self.zorder, 
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round4,pad=1'))
        self.zorder += 1

    def _beautify(self, fig, axes, groups, colors):
        xticks = range(int(self.config['max_xlim']) + 1)
        yticks = np.arange(1, int(self.config['max_ylim']) + 1) + 0.5
        ylabels = [f'{i:>2d}' for i in range(1, int(self.config['max_ylim']) + 1)]
        for ax in axes:
            ax.grid(axis='x', linestyle='--', zorder=1)
            ax.set_xlim(0, self.config['max_xlim'])
            ax.set_ylim(1, self.config['max_ylim'])
            ax.set_xticks(xticks, xticks, fontsize=self.config['font.size'])
            ax.set_yticks(yticks, ylabels, fontsize=self.config['font.size'])
        
        for label in axes[0].get_xticklabels():
            if label.get_text().isdigit():
                label.set_visible(False)
        axes[1].set_xlabel('Time', fontsize=self.config['font.size'])

        for group, idx in groups.items():
            axes[idx].set_facecolor(colors.get(group, 'white'))
            axes[idx].set_ylabel(f"{group.title()} {self.config['ylabel']}", fontsize=self.config['font.size'])
        fig.tight_layout()
    
    def _update_config(self, tasks):
        if not "max_xlim" in self.config:
            self.config['max_xlim'] = max([t.finish_time for t in tasks])
        if not "max_ylim" in self.config:
            self.config['max_ylim'] = max([t.idx for t in tasks]) + 1
        self.zorder = 1
    
    def _create_figure(self):
        fig, axes = plt.subplots(
            nrows=2, ncols=1, figsize=(self.config['max_xlim'], self.config['max_ylim']), 
            dpi=self.config['dpi'])
        return fig, axes

    def draw(self, tasks: List[Task], events: List[Event], period: Period, groups, colors):
        self._update_config(tasks)
        fig, axes = self._create_figure()
        for task in tasks:
            self._draw_task(
                task, ax=axes[groups.get(task.group, 0)], 
                color=colors.get(task.class_name, 'white'))
        for event in events:
            self._draw_event(event, axes)
        self._draw_period(period, axes)
        self._beautify(fig, axes, groups, colors)
        return fig
