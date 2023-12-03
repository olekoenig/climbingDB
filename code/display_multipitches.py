#!/usr/bin/env python3

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from climbingQuery import ClimbingQuery
from grade import Grade

plt.rcParams['text.usetex'] = True


def main():
    db = ClimbingQuery()
    mp = db.getMultipitches().sort_values(by = ["ole_grade"], ascending = False)

    plt.figure(figsize=(.37*len(mp.name), 7))

    # Fix me: Why doesn't one min work? Some weird slicing?
    min_grade = min(mp.pitches_ole_grade.min())
    max_grade = max(mp.pitches_ole_grade.max())

    # to define own cmap, see https://stackoverflow.com/questions/53754012/create-a-gradient-colormap-matplotlib
    norm = matplotlib.colors.Normalize(vmin=min_grade, vmax=max_grade, clip=True)
    mapper = cm.ScalarMappable(norm=norm, cmap=cm.get_cmap('RdYlGn_r'))

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

            title = '{} ({})\n {}'.format(row['name'], row['grade'], row['area'])

            plt.bar(title, avg_pitch_length, **kwargs)
            # plt.text(title, c*avg_pitch_length+avg_pitch_length//2, pitch, ha = 'center')
            
    plt.xticks(rotation = 90)
    plt.ylabel("Length [m]")
    plt.tight_layout()
    plt.savefig("multipitches.pdf")
        

    
if __name__ == "__main__":
    main()
        
