from climbingdb.models import SessionLocal, User, Route, Ascent
import pandas as pd


def get_user_statistics():
    """Query user statistics including route counts per discipline."""
    session = SessionLocal()

    try:
        # Get all users with route counts
        users = session.query(User).all()

        user_data = []
        for user in users:
            # Count routes per discipline
            sportclimb_count = session.query(Ascent).join(Ascent.route).filter(
                Ascent.user_id == user.id,
                Route.discipline == "Sportclimb"
            ).count()

            boulder_count = session.query(Ascent).join(Ascent.route).filter(
                Ascent.user_id == user.id,
                Route.discipline == "Boulder"
            ).count()

            multipitch_count = session.query(Ascent).join(Ascent.route).filter(
                Ascent.user_id == user.id,
                Route.discipline == "Multipitch"
            ).count()

            total_routes = sportclimb_count + boulder_count + multipitch_count

            # Get hardest route
            hardest = session.query(Ascent).join(Ascent.route).filter(
                Ascent.user_id == user.id
            ).order_by(Route.consensus_ole_grade.desc()).first()

            user_data.append({
                'User ID': user.id,
                'Username': user.username,
                'Email': user.email if user.email else '',
                'Total Routes': total_routes,
                'Sport': sportclimb_count,
                'Boulder': boulder_count,
                'Multipitch': multipitch_count,
                'Hardest Grade': hardest.grade if hardest else '',
                'Created': user.created_at.strftime('%Y-%m-%d') if user.created_at else ''
            })

        df = pd.DataFrame(user_data)
        return df

    finally:
        session.close()


def print_user_stats():
    """Print formatted user statistics."""
    print("=" * 80)
    print("User Statistics")
    print("=" * 80)

    df = get_user_statistics()

    print(f"\nTotal Users: {len(df)}")
    print(f"Total Routes in Database: {df['Total Routes'].sum()}")
    print(f"\nBreakdown by Discipline:")
    print(f"  Sport:      {df['Sport'].sum()}")
    print(f"  Boulder:    {df['Boulder'].sum()}")
    print(f"  Multipitch: {df['Multipitch'].sum()}")

    print("\n" + "=" * 80)
    print("Per-User Breakdown")
    print("=" * 80)
    print()
    print(df.to_string(index=False))
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print_user_stats()