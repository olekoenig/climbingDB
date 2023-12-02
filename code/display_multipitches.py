import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm


from climbingQuery import ClimbingQuery
from grade import Grade

plt.rcParams['text.usetex'] = True


def main():
    db = ClimbingQuery()
    mp = db.getMultipitches().sort_values(by = ["length"], ascending = False)

    plt.figure(figsize=(15, 7))
    
    for index, row in mp.iterrows():
        pitches = row.pitches.split(",")

        print(row.length)
        avg_pitch_length = row.length / len(pitches)

        # put this into ClimbingQuery._import_routes?
        pitches_ole_grades = list(Grade(pitch.strip("()")).conv_grade() for pitch in pitches)
        
        max_grade = max(pitches_ole_grades)
        min_grade = min(pitches_ole_grades)

        norm = matplotlib.colors.Normalize(vmin=min_grade, vmax=max_grade, clip=True)
        mapper = cm.ScalarMappable(norm=norm, cmap=cm.RdYlGn)

        for c, pitch in enumerate(pitches):
            ole_grade = Grade(pitch).conv_grade()
            
            color = mapper.to_rgba(pitches_ole_grades[c])

            kwargs = {'bottom': c * avg_pitch_length,
                      'color': color,
                      'alpha': 1,
                      'edgecolor': "black"
                      }

            # if "(" in pitch:
            #     kwargs['alpha'] = 0.4

            title = '{} ({})\n {}'.format(row['name'], row['grade'], row['area'])

            plt.bar(title, avg_pitch_length, **kwargs)

        plt.xticks(rotation=90)
        plt.ylabel("Length [m]")
        plt.tight_layout()
        plt.savefig("multipitches.pdf")
        exit()

    
if __name__ == "__main__":
    main()
        
