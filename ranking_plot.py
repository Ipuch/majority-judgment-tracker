import plotly.graph_objects as go
from seaborn import color_palette
from utils import get_intentions_colheaders, get_candidates, get_grades, rank2str
from plots import _add_election_date, load_colors, _extended_name_annotations
from pandas import DataFrame
from colors import load_colors


class RankingPlot:
    def __init__(
        self,
        df,
        fig: go.Figure = None,
        on_rolling_data: bool = False,
        source: str = None,
        sponsor: str = None,
        show_best_grade: bool = True,
        show_rank: bool = True,
        show_no_opinion: bool = True,
        show_grade_area: bool = True,
        breaks_in_names: bool = True,
        annotations: dict = None,
        rank_key: str = "rang",
        field_key: str = "candidat",
        method: str = "jugement majoritaire",
        row=None,
        col=None,
    ):
        self.df = df.sort_values(by="fin_enquete")
        self.on_rolling_data = on_rolling_data
        self.source = source
        self.sponsor = sponsor
        self.show_best_grade = show_best_grade
        self.show_rank = show_rank
        self.show_no_opinion = show_no_opinion
        self.show_grade_area = show_grade_area
        self.breaks_in_names = breaks_in_names
        self.fig = go.Figure() if fig is None else fig
        self.annotations = [] if annotations is None else annotations
        self.row = row
        self.col = col
        self.xref = f"x{self.col}" if self.col is not None else None
        self.yref = f"y{self.row}" if self.row is not None else None
        self.rank_key = rank_key
        self.field_key = field_key
        self.method = method
        self.show_legend = True if self.field_key == "methode" else False
        self.show_annotations = True if self.field_key == "candidat" else False
        self.visible_yaxis = False if self.field_key == "candidat" else True
        self.y_offset = False if self.field_key == "candidat" else True
        self.colors = load_colors(key=self.field_key)
        if self.on_rolling_data:
            self._set_rolling_data(df)
        if show_grade_area:
            self.plot_grade_area()
        self.legend_title = "Mentions" if self.field_key == "candidat" else "Méthodes"

        self.size_annotations = 12
        self.items = df[self.field_key].unique()
        self.n_items = len(self.items)
        for i, item in enumerate(self.items):
            # set an offset around the value to avoid overlapping
            y_offset = (-self.n_items / 2 + +1 / 2 + i) * 0.05 if self.y_offset else 0
            sub_df = df[df[self.field_key] == item]
            self.plot_rank_line(sub_df=sub_df, item=item, y_offset=y_offset)
            if self.show_annotations:
                self._add_annotations(sub_df=sub_df, item=item)

        self._automatic_title()
        self.fig.update_layout(
            title=self.title,
            title_x=0.5,
            yaxis=dict(
                autorange="reversed",
                tick0=1,
                dtick=1,
                visible=self.visible_yaxis,
                gridwidth=1,
                showgrid=True,
                gridcolor="grey",
                ticksuffix="  ",
            ),
            annotations=annotations,
            plot_bgcolor="white",
            showlegend=True,
            width=1200,
            height=800,
            legend_title_text=self.legend_title,
            autosize=True,
            legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.05),
        )

        self._add_election_date(y=0.25, xshift=10)
        self._add_image_to_fig(x=1.00, y=1.05, sizex=0.10, sizey=0.10, xanchor="right")

    def _set_rolling_data(self, df):
        if "rang_glissant" not in df.columns:
            raise ValueError("This dataframe hasn't been smoothed with rolling average.")
        self.df[self.rank_key] = self.df[f"{self.rank_key}_glissant"]
        self.df["mention_majoritaire"] = self.df["mention_majoritaire_glissante"]

    def plot_grade_area(self):
        grades = get_grades(self.df)
        nb_grades = len(grades)
        c_rgb = color_palette(palette="coolwarm", n_colors=nb_grades)
        for g, c in zip(grades, c_rgb):
            temp_df = self.df[self.df["mention_majoritaire"] == g]
            if not temp_df.empty:
                c_alpha = str(f"rgba({c[0]},{c[1]},{c[2]},0.2)")
                x_date = temp_df["fin_enquete"].unique().tolist()
                y_upper = []
                y_lower = []
                for d in x_date:
                    y_upper.append(temp_df[temp_df["fin_enquete"] == d][self.rank_key].min() - 0.5)
                    y_lower.append(temp_df[temp_df["fin_enquete"] == d][self.rank_key].max() + 0.5)

                self.fig.add_scatter(
                    x=x_date + x_date[::-1],  # x, then x reversed
                    y=y_upper + y_lower[::-1],  # upper, then lower reversed
                    fill="toself",
                    fillcolor=c_alpha,
                    line=dict(color="rgba(255,255,255,0)"),
                    hoverinfo="skip",
                    showlegend=True,
                    name=g,
                    row=self.row,
                    col=self.col,
                )

    def plot_dot(self, x: DataFrame, y: DataFrame, name: str, color: str):
        self.fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="markers",
                name=name,
                marker=dict(color=color),
                showlegend=False,
                legendgroup=name,
            ),
            row=self.row,
            col=self.col,
        )

    def plot_dot_annotation(self, x: DataFrame, y: DataFrame, label, xanchor: str, item: str):
        xshift = 10 if xanchor == "left" else -10
        self.fig["layout"]["annotations"] += (
            dict(
                x=x,
                y=y,
                xanchor=xanchor,
                xshift=xshift,
                yanchor="middle",
                text=f"{label}",
                font=dict(family="Arial", size=self.size_annotations, color=self.colors[item]["couleur"]),
                showarrow=False,
                xref=self.xref,
                yref=self.yref,
            ),
        )

    def plot_rank_line(self, sub_df: DataFrame, item: str, y_offset: float):
        self.fig.add_trace(
            go.Scatter(
                x=sub_df["fin_enquete"],
                y=sub_df[self.rank_key] + y_offset,
                mode="lines",
                name=item,
                marker=dict(color=self.colors[item]["couleur"]),
                legendgroup=item,
                showlegend=self.show_legend,
            ),
            row=self.row,
            col=self.col,
        )

        # first dot
        self.plot_dot(
            x=sub_df["fin_enquete"].iloc[0:1],
            y=sub_df[self.rank_key].iloc[0:1] + y_offset,
            name=item,
            color=self.colors[item]["couleur"],
        )
        # final dot
        self.plot_dot(
            x=sub_df["fin_enquete"].iloc[-1:],
            y=sub_df[self.rank_key].iloc[-1:] + y_offset,
            name=item,
            color=self.colors[item]["couleur"],
        )

    def _add_annotations(self, sub_df: DataFrame, item: str):
        # PREPARE ANNOTATIONS
        # name with break btw name and surname
        name_label = _extended_name_annotations(
            sub_df,
            candidate=item,
            show_rank=False,
            show_best_grade=False,
            show_no_opinion=False,
            breaks_in_names=self.breaks_in_names,
        )

        # first dot annotation
        # plot only if the final dot is not on the same date as the first dot
        # if sub_df["fin_enquete"].iloc[-1] != sub_df["fin_enquete"].iloc[0]:
        self.plot_dot_annotation(
            x=sub_df["fin_enquete"].iloc[0],
            y=sub_df[self.rank_key].iloc[0],
            label=name_label,
            xanchor="right",
            item=item,
        )

        # Nice name label
        extended_name_label = _extended_name_annotations(
            sub_df,
            candidate=item,
            show_rank=self.show_rank,
            show_best_grade=self.show_best_grade,
            show_no_opinion=self.show_no_opinion,
            breaks_in_names=self.breaks_in_names,
        )

        # last dot annotation
        # plot only if the last dot has the same date the maximum date of all polls
        if self.df["fin_enquete"].max() == sub_df["fin_enquete"].iloc[-1]:
            self.plot_dot_annotation(
                x=sub_df["fin_enquete"].iloc[-1],
                y=sub_df[self.rank_key].iloc[-1],
                label=extended_name_label,
                xanchor="left",
                item=item,
            )

    def _add_election_date(self, y: float = 34, xshift: float = 0, row: int = None, col: int = None):
        """
        Add the date of the election to the figure.

        Parameters
        ----------
        y : float, optional
            y position of the date. The default is 34.
        xshift : float, optional
            xshift of the date. The default is 0.
        row : int, optional
            row of the subplot. The default is None.
        col : int, optional
            column of the subplot. The default is None.
        """

        self.fig.add_vline(x="2022-04-10", line_dash="dot", row=row, col=col, line=dict(color="rgba(0,0,0,0.5)"))
        self.fig["layout"]["annotations"] += (
            dict(
                x="2022-04-10",
                y=y,
                xanchor="left",
                xshift=xshift,
                yanchor="middle",
                text="1er Tour",
                font=dict(family="Arial", size=12),
                showarrow=False,
                xref=self.xref,
                yref=self.yref,
            ),
        )

    def _add_image_to_fig(self, x: float, y: float, sizex: float, sizey: float, xanchor: str = "left"):
        """
        Add mieux voter logo to the figure

        Parameters
        ----------
        x : float
            x position of the logo
        y : float
            y position of the logo
        sizex : float
            x size of the logo
        sizey : float
            y size of the logo
        xanchor : str
            x anchor of the logo (left, center, right)
        Returns
        -------
        The figure with the logo
        """
        self.fig.add_layout_image(
            dict(
                source="https://raw.githubusercontent.com/MieuxVoter/majority-judgment-tracker/main/icons/logo.svg",
                xref="paper",
                yref="paper",
                x=x,
                y=y,
                sizex=sizex,
                sizey=sizey,
                xanchor=xanchor,
                yanchor="bottom",
            )
        )

    def set_title(self, title: str):
        """
        Set the title of the figure.

        Parameters
        ----------
        title : str
            Title of the figure.
        """
        self.fig["layout"]["title"] = title

    def _automatic_title(self):
        source_str = f"source: {self.source}" if self.source is not None else ""
        source_str += ", " if self.sponsor is not None else ""
        sponsor_str = f"commanditaire: {self.sponsor}" if self.sponsor is not None else ""
        candidate_str = "des candidats" if self.field_key == "candidat" else f"de {self.df.candidat.unique()[0]}"
        method_str = f"au {self.method}" if self.field_key == "candidat" else "selon différents modes de scrutin"

        date = self.df["fin_enquete"].max()
        self.title = (
            f"<b>Classement {candidate_str} à l'élection présidentielle 2022<br>{method_str}</b><br>"
            + f"<i>{source_str}{sponsor_str}, dernier sondage: {date}.</i>"
        )

    def show(self):
        self.fig.show()
