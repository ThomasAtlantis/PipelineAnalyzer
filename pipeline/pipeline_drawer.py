from .pipeline_parser import Task, Event, Period
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import ArrowStyle
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as ticker
from typing import List
import numpy as np


class DiagramDrawer:
    def __init__(self, **kwargs):
        self.config = {
            'fontsize': 18,
            'dpi': 80,
            'ylabel': "",
            **kwargs
        }
    
    def _draw_task(self, task: Task, ax, color, zorder):
        ax.add_patch(patches.Rectangle(
            xy=(task.start_time, task.idx), width=task.duration, height=1, 
            edgecolor='black', facecolor=color, zorder=zorder))
        ax.text(
            x=task.start_time + task.duration / 2, y=task.idx + 0.5, s=task.label, 
            ha='center', va='center', color='black', fontsize=self.config['fontsize'], 
            zorder=zorder)
    
    def _draw_event(self, event: Event, axes, groups):
        ax_idx = groups.get(event.task.group, 0)
        annote_y = -0.5 if ax_idx == 0 else self.config['max_ylim'] + 0.5 
        for ax in axes:
            ax.axvline(x=event.time, color='black', linestyle='--', zorder=1)
        axes[ax_idx].text(
            x=event.time, y=annote_y, s=event.label, 
            ha='center', va='center', color='black', fontsize=self.config['fontsize'], 
            bbox=dict(facecolor='none', edgecolor='none'), zorder=2)
    
    def _draw_period(self, period: Period, axes):
        if period is None:
            return
        annote_y = 0.5
        arrowprops = {
            "color": "black", 
            "arrowstyle": ArrowStyle.CurveFilledAB(
                head_width=0.3, 
                head_length=1.5
            )
        }
        axes[0].annotate(
            text='', xy=(period.start_time, annote_y), xytext=(period.finish_time, annote_y), 
            arrowprops=arrowprops)
        axes[0].text(
            x=period.start_time + (period.finish_time - period.start_time) / 2, y=annote_y, 
            s=period.label, fontsize=self.config['fontsize'],
            ha='center', va='center', color='black', 
            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

    def _beautify(self, fig, axes, groups, colors):
        xticks = range(int(self.config['max_xlim']) + 1)
        for ax in axes:
            ax.grid(linestyle='-', zorder=1, alpha=0.5)
            ax.set_xlim(0, self.config['max_xlim'])
            ax.set_ylim(0, self.config['max_ylim'])
            ax.set_xticks(xticks, xticks, fontsize=self.config['fontsize'])

            ax.yaxis.set_major_locator(MultipleLocator(1))
            ax.yaxis.set_minor_locator(MultipleLocator(0.5))
            ax.yaxis.set_major_formatter(ticker.NullFormatter())
            ax.yaxis.set_minor_formatter(ticker.FuncFormatter(lambda value, index: f"{value-0.5:>2.0f}" if value != 0.5 else ""))
            ax.tick_params(axis='y', which='minor', tick1On=False, tick2On=False)
            ax.tick_params(axis='y', which='minor', labelsize=self.config['fontsize'])
        
        for label in axes[0].get_xticklabels():
            label.set_visible(False)

        axes[0].spines['bottom'].set_visible(False)
        axes[1].spines['top'].set_visible(False)
        axes[0].tick_params(axis='x', which='both', length=0)
        axes[1].set_xlabel('Time', fontsize=self.config['fontsize'])

        for group, idx in groups.items():
            axes[idx].set_facecolor(colors.get(group, 'white'))
            axes[idx].set_ylabel(f"{group.title()} {self.config['ylabel']}", fontsize=self.config['fontsize'])
        fig.tight_layout()
    
    def _update_config(self, tasks):
        if not "max_xlim" in self.config:
            self.config['max_xlim'] = max([t.finish_time for t in tasks])
        if not "max_ylim" in self.config:
            self.config['max_ylim'] = max([t.idx for t in tasks]) + 1
    
    def _create_figure(self):
        fig, axes = plt.subplots(
            nrows=2, ncols=1, figsize=(self.config['max_xlim'], self.config['max_ylim']), 
            dpi=self.config['dpi'])
        return fig, axes

    def draw(self, tasks: List[Task], events: List[Event], period: Period, groups, colors):
        self._update_config(tasks)
        fig, axes = self._create_figure()
        sorted_tasks = sorted(tasks, key=lambda t: t.start_time)
        for zorder, task in enumerate(sorted_tasks):
            self._draw_task(
                task, ax=axes[groups.get(task.group, 0)], 
                color=colors.get(task.class_name, 'white'), zorder=zorder)
        for event in events:
            self._draw_event(event, axes, groups)
        self._draw_period(period, axes)
        self._beautify(fig, axes, groups, colors)
        return fig
