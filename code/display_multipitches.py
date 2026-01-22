#!/usr/bin/env python3

import shutil
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from climbingQuery import ClimbingQuery
from grade import Ole_to_French

if shutil.which("latex"):
    plt.rcParams['text.usetex'] = True


def create_multipitch_visualization(mp_dataframe):
    mp = mp_dataframe.sort_values(by=["ole_grade"], ascending=False)

    # Fix me: Why doesn't one min work? Some weird slicing?
    min_grade = min(mp.pitches_ole_grade.min())
    max_grade = max(mp.pitches_ole_grade.max())

    # to define own cmap, see https://stackoverflow.com/questions/53754012/create-a-gradient-colormap-matplotlib
    norm = matplotlib.colors.Normalize(vmin=min_grade, vmax=max_grade, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=matplotlib.colormaps.get_cmap('RdYlGn_r'))

    fig, ax = plt.subplots(figsize=(.37*len(mp.name), 7))
    
    for index, row in mp.iterrows():
        avg_pitch_length = row.length / len(row.pitches_ole_grade)

        for c, pitch in enumerate(row.pitches_ole_grade):
            color = mapper.to_rgba(row.pitches_ole_grade[c])

            kwargs = {'bottom': c * avg_pitch_length,
                      'color': color,
                      'alpha': 1,
                      'edgecolor': "black",
                      'hatch': None
                      }
            
            if row.pitches != "":
                pitch = row.pitches.split(",")[c]
                if "(" in pitch:
                    # kwargs['alpha'] = 0.2
                    kwargs['hatch'] = "oo"

            kwargs['alpha'] = 0.2 if row.project == "X" else 1

            grade = row['grade'] if row['style'] == "" else "{} {}".format(row['grade'], row['style'])
            title = '{} ({})\n {}'.format(row['name'], grade, row['area'])

            ax.bar(title, avg_pitch_length, **kwargs)
            # plt.text(title, c*avg_pitch_length+avg_pitch_length//2, pitch, ha = 'center')
    
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(.99, 0.95, "Solid: Lead\n Hashed: Follow\n Transparent: Project", transform=ax.transAxes, fontsize=10,
            va='top', ha="right", bbox=props)

    plt.title("Multipitch Routebook Ole")
    plt.xticks(rotation = 90)
    plt.ylabel("Length [m]")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='1%', pad=0.05)
    tics = [11, 15, 18, 20, 22, 24, 26, 28, 29.5]
    ticlabels = [Ole_to_French[tic] for tic in tics]
    cbar = fig.colorbar(mapper, cax = cax, orientation='vertical')
    cbar.set_ticks(tics)
    cbar.set_ticklabels(ticlabels)

    plt.tight_layout()
    return fig
        
def main():
    db = ClimbingQuery()
    mp = db.get_multipitches()
    fig = create_multipitch_visualization(mp)
    plt.savefig("multipitches.pdf")
    
if __name__ == "__main__":
    main()
        
