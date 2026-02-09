import shutil
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

from climbingdb.grade import Ole_to_French, Grade

if shutil.which("latex"):
    plt.rcParams['text.usetex'] = True


def plot_multipitches(mp_dataframe):
    mp = mp_dataframe.sort_values(by=["ole_grade"], ascending=False)

    min_grade = mp['ole_grade'].min()
    max_grade = mp['ole_grade'].max()

    # to define own cmap, see https://stackoverflow.com/questions/53754012/create-a-gradient-colormap-matplotlib
    norm = matplotlib.colors.Normalize(vmin=min_grade, vmax=max_grade, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=matplotlib.colormaps.get_cmap('RdYlGn_r'))

    xwidth = max(.37 * len(mp.name), 15)
    fig, ax = plt.subplots(figsize=(xwidth, xwidth/3))

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

            if row.pitches and row.pitches[c]["led"] == True:
                # kwargs['alpha'] = 0.2
                kwargs['hatch'] = "oo"

            kwargs['alpha'] = 0.2 if row.is_project else 1

            grade = row['grade'] if row['style'] == "" else "{} {}".format(row['grade'], row['style'])
            title = '{} ({})\n {}'.format(row['name'], grade, row['area'])

            ax.bar(title, avg_pitch_length, **kwargs)
            # plt.text(title, c*avg_pitch_length+avg_pitch_length//2, pitch, ha = 'center')

    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(.99, 0.95, "Solid: Lead\n Hashed: Follow\n Transparent: Project", transform=ax.transAxes, fontsize=10,
            va='top', ha="right", bbox=props)

    plt.title("Multipitch Routebook Ole")
    plt.xticks(rotation=90)
    plt.ylabel("Length [m]")

    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='1%', pad=0.05)
    tics = [11, 15, 18, 20, 22, 24, 26, 28, 29.5]
    ticlabels = [Ole_to_French[tic] for tic in tics]
    cbar = fig.colorbar(mapper, cax=cax, orientation='vertical')
    cbar.set_ticks(tics)
    cbar.set_ticklabels(ticlabels)

    plt.tight_layout()
    return fig

def plot_grade_pyramid(routes, grades, sandbaggers_choice="Round down",
                       title="Grade Distribution", figsize=(15, 5)):
    # Get min and max ole_grade from the filtered routes
    min_ole = routes['ole_grade'].min()
    max_ole = routes['ole_grade'].max()

    # Filter grades to only include those within the actual data range
    grades = [g for g in grades if min_ole <= Grade(g).conv_grade() <= max_ole]

    # Convert grades to ole_grade values
    ole_grades = [Grade(g).conv_grade() for g in grades]

    # Count routes in each grade bin
    counts = []
    lower_grade = -1
    for ii in range(len(grades)):
        current_grade = ole_grades[ii]
        next_grade = ole_grades[ii+1] if ii < len(grades)-1 else 100

        if sandbaggers_choice == "Round down":
            count = len(routes[(routes['ole_grade'] >= current_grade) & (routes['ole_grade'] < next_grade)])
        else:
            count = len(routes[(routes['ole_grade'] > lower_grade) & (routes['ole_grade'] <= current_grade)])
        lower_grade = current_grade
        counts.append(count)

    fig, ax = plt.subplots(figsize=figsize)

    # Use indices for x-axis (equidistant spacing instead of ole_grade)
    x_pos = range(len(grades))

    colors = plt.cm.RdYlGn_r([i / len(grades) for i in range(len(grades))])
    bars = ax.bar(x_pos, counts, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Grade', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Routes', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(grades, rotation=45, ha='right')

    # Add count labels on top of bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        if count > 0:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{int(count)}',
                    ha='center', va='bottom', fontsize=9)

    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    from climbingdb.services.climbing_service import ClimbingService

    db = ClimbingService()

    routes = db.get_filtered_routes()
    sport_grades = ["4a", "5a", "6a", "6b", "6c", "7a", "7a+", "7b", "7b+",
                    "7c", "7c+", "8a", "8a+", "8b", "8b+", "8c", "8c+", "9a"]
    fig = plot_grade_pyramid(routes, grades = sport_grades, title="My Sport Climbing Grade Pyramid")
    fig.savefig("grade_pyramid.pdf", dpi=300, bbox_inches='tight')

    boulders = db.get_boulders()
    boulder_grades = ['V0', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8',
                      'V9', 'V10', 'V11', 'V12', 'V13', 'V14', 'V15']
    fig_boulder = plot_grade_pyramid(boulders, grades = boulder_grades, title="My Boulder Grade Pyramid")
    fig_boulder.savefig("boulder_pyramid.pdf", dpi=300, bbox_inches='tight')

    mp = db.get_multipitches()
    fig = plot_multipitches(mp)
    plt.savefig("multipitches.pdf")
