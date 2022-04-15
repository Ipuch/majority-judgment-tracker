from ranking_plot import RankingPlot
import pandas as pd

df_ow = pd.read_csv("opinion_way_method_of_voting.csv", na_filter=False)

methods = ["jugement majoritaire", "condorcet", "borda", "vote par assentiment simulé", "vote par note"]
method_labels = [
    "Jugement majoritaire",
    "scrutin de Condorcet",
    "scrutin de Borda",
    "Vote par assentiment simulé",
    "Vote par note",
]

# for m, ml in zip(methods, method_labels):
#     sub_df = df_ow[df_ow["methode"] == m]
#     rp = RankingPlot(df=sub_df,
#                      source="Opinion Way",
#                      sponsor="Mieux Voter",
#                      show_grade_area=False,
#                      breaks_in_names=True,
#                      rank_key="rang",
#                      field_key="candidat",
#                      method=ml)
#
#     rp.show()
#     rp.fig.write_image(f"all_{m}.png")

candidates = df_ow["candidat"].unique()

for c in candidates:
    sub_df = df_ow[df_ow["candidat"] == c]
    rp = RankingPlot(
        df=sub_df,
        source="Opinion Way",
        sponsor="Mieux Voter",
        show_grade_area=False,
        breaks_in_names=True,
        rank_key="rang",
        field_key="methode",
    )

    rp.show()
    rp.fig.write_image(f"c_{c}.png")
    rp.fig.write_html(f"c_{c}.html", config=dict(displaylogo=False))
