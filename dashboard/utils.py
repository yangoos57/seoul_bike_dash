from tkinter import font
from bs4 import BeautifulSoup
import plotly.express as px
import plotly.graph_objects as go
import plotly
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
import pandas as pd
import numpy as np
import base64
import ast
from io import BytesIO
from matplotlib import font_manager, rc

matplotlib.use("Agg")
rc("font", family="AppleGothic")
plt.rcParams["axes.unicode_minus"] = False

# def time_check(func):
#     def wrapper():
#         start_in = time.time()
#         func()
#         print(func.__name__, '결과', start_in-time.time())
#     return wrapper

################## 기본 함수
def get_graph():
    buffer = BytesIO()
    plt.savefig(
        buffer, format="png", bbox_inches="tight", transparent=True, pad_inches=0
    )
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode("utf-8")
    buffer.close()
    return graph


def haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2

    c = 2 * np.arcsin(np.sqrt(a))
    m = 6367 * c * 1000
    return m


def raw_data(query_data, val):
    quert_st_id1 = query_data[query_data["st_id1"] == val]
    quert_st_id2 = query_data[query_data["st_id2"] == val]
    filtered_data = pd.concat([quert_st_id1, quert_st_id2], axis=0).drop_duplicates()
    filtered_data.drop(columns="index", inplace=True)
    bm = (filtered_data["st_id1"] == val) & (filtered_data["st_id2"] == val)
    filtered_data = filtered_data[~bm]
    # filtered_data.reset_index(drop=True, inplace=True)

    # 대여
    filtered_data_start = filtered_data[
        (filtered_data["st_id1"] == val) & (filtered_data["st_id2"] != val)
    ]

    # 반납
    filtered_data_end = filtered_data[
        (filtered_data["st_id2"] == val) & (filtered_data["st_id1"] != val)
    ]

    return [filtered_data, filtered_data_end, filtered_data_start]


def day_rent(filtered_data):
    # 일별 자전거 대여
    filtered_data = filtered_data[0]
    filtered_data["weekday"] = filtered_data["date"].dt.weekday
    data = filtered_data.groupby("weekday").size()
    data_numpy = data.to_numpy()

    # max 요일
    max_value = np.where(data_numpy == data_numpy.max())[0][0]
    print("max_value:", max_value)

    # 높이 normalize 후 0.5 더함( 0.5는 막대 길이를 의미함)
    height = list(
        map(
            lambda x: round(
                ((x - data_numpy.min()) / (data_numpy.max() - data_numpy.min())) + 0.5,
                2,
            ),
            data_numpy,
        )
    )

    # 사각형 정보
    bars = []
    for num, h in enumerate(height):
        ist = [num, 0, h, 0.82]  # x,y,h,w
        bars.append(ist)
    # 날짜
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    # days = ["월","화","수","목","금","토","일"]

    # plot
    fig, ax = plt.subplots(figsize=(8, 4))

    # bar = rect
    for num, (bar, days) in enumerate(zip(bars, days)):
        x = bar[0]
        y = bar[1]
        h = bar[2]
        w = bar[3]
        # max
        if num == max_value:
            color = "#35C768"  # full color, font-color
        # 나머지
        else:
            color = "#EBEEF2"  # full color, font-color

        bbox = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=-0.01,rounding_size=0.0",
            ec="none",
            fc=color,
            mutation_aspect=0.5,
        )
        ax.add_patch(bbox)

        # 요일 넣기(padding고려해서 num으로 조정)
        if days == "Fri":
            plt.text(
                x + 0.25,
                y - 0.1,
                days,
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )
        else:
            plt.text(
                x + 0.15,
                y - 0.1,
                days,
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        # 개수 넣기
        if data[num] > 10000:
            plt.text(
                x + 0.02,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        elif 10000 > data[num] > 1000:
            plt.text(
                x + 0.07,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        else:
            plt.text(
                x + 0.2,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

    plt.xlim(-0.2, 7)  # 넓이가 0.8이라서 그럼
    plt.ylim(-0.2, 1.5)
    plt.axis("off")
    graph = get_graph()
    plt.close()
    return graph


# 반납 : filtered_data_end(=num 1), 대여 : filtered_data_start(=num 2)


def time_rent(filtered_data, days="weekday"):
    # date 나눔
    time_data = filtered_data[0]["date"]

    # 평일 주말 구분
    if days == "weekday":
        days = time_data.dt.weekday.isin([0, 1, 2, 3, 4])  ##weekday
    else:
        days = time_data.dt.weekday.isin([5, 6])  ##weekend

    a = time_data[days].dt.hour
    bins = [-1, 5, 8, 11, 14, 17, 20, 23]
    time = ["0-6", "6-9", "9-12", "12-15", "15-18", "18-21", "21-24"]
    data = a.groupby(pd.cut(a, bins=bins, labels=time)).size()
    data_numpy = data.to_numpy()

    # max 요일
    max_value = np.where(data_numpy == data_numpy.max())[0][0]

    # 높이 normalize 후 0.5 더함( 0.5는 막대 길이를 의미함)
    height = list(
        map(
            lambda x: round(
                ((x - data_numpy.min()) / (data_numpy.max() - data_numpy.min())) + 0.5,
                2,
            ),
            data_numpy,
        )
    )

    bars = []
    for num, h in enumerate(height):
        ist = [num, 0, h, 0.82]  # x,y,h,w
        bars.append(ist)

    # plot
    fig, ax = plt.subplots(figsize=(8, 4))

    # bar = rect
    for num, (bar, time) in enumerate(zip(bars, time)):
        x = bar[0]
        y = bar[1]
        h = bar[2]
        w = bar[3]
        # max
        if num == max_value:
            color = "#35C768"  # bg-color
        # 나머지
        else:
            color = "#EBEEF2"  # bg-color

        bbox = patches.FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=-0.01,rounding_size=0.0",
            ec="none",
            fc=color,
            mutation_aspect=0.5,
        )
        ax.add_patch(bbox)

        # 요일 넣기(padding고려해서 num으로 조정)
        if len(time) > 4:
            plt.text(
                x + 0.1,
                y - 0.1,
                time,
                fontdict={"fontsize": 13, "color": (0, 0, 0, 0.7)},
            )
        else:
            plt.text(
                x + 0.15,
                y - 0.1,
                time,
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        # 개수 넣기
        if data[num] > 10000:
            plt.text(
                x + 0.02,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        elif 10000 > data[num] > 1000:
            plt.text(
                x + 0.07,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

        else:
            plt.text(
                x + 0.2,
                h + 0.02,
                data[num],
                fontdict={"fontsize": 14, "color": (0, 0, 0, 0.7)},
            )

    plt.xlim(-0.2, 7)  # 넓이가 0.8이라서 그럼
    plt.ylim(-0.2, 1.5)
    plt.axis("off")

    graph = get_graph()
    plt.close()
    return graph


def total_rent(filtered_data):
    # 데이터 정제
    a = len(filtered_data[1])
    b = len(filtered_data[2])
    percent = round((a / (a + b) * 100), 1)

    ratio = [percent, 100 - percent]
    colors = ["#35C768", "#35c76880"]

    plt.figure(figsize=(3, 3))
    plt.pie(
        ratio,
        startangle=270,
        autopct="%.1f%%",
        colors=colors,
        textprops=dict(color="w", fontsize=14),
    )
    # texts = ["출발", "도착"]
    # patches = [
    #     plt.plot(
    #         [],
    #         [],
    #         marker="o",
    #         ms=10,
    #         ls="",
    #         mec=None,
    #         color=colors[i],
    #         label="{:s}".format(texts[i]),
    #     )[0]
    #     for i in range(len(texts))
    # ]
    # plt.legend(
    #     handles=patches,
    #     bbox_to_anchor=(0.98, 0.95),
    #     loc="center",
    #     facecolor="white",
    #     framealpha=0,
    #     fontsize=12,
    # )
    graph = get_graph()
    plt.close()
    return graph


class recommend_sub_station:
    def __init__(self, filtered_data, stat_id, near_sub, station, bike_info, num=20):
        """

        해당 대여소에서 자주 이용하는 지하철역과 그 주변에 있는 따릉이 대여소를 추천하는 매서드임.
        filtered_data는 원하는 대여소가 sorting 된 DataFrame이 필요함.

        filter_start는 "대여소" 또는 "역"만 올 수 있음.

        """
        self.stat_id = stat_id
        self.near_sub = near_sub
        self.station = station
        self.filtered_data = filtered_data
        self.bike_info = bike_info

        print(self.bike_info.query("value == @self.stat_id").label)
        """
        개별 대여소별로 해당 대여소와 얼마나 교류가 있는지 확인한다.
        """

        # ex) 기준대여소 to 다른 대여소 (1to2)
        total_num_left = filtered_data[filtered_data["st_id1"] == stat_id][
            "st_id2"
        ].value_counts()

        # ex) 다른 대여소 to 기준대여소 (2to1)
        total_num_right = filtered_data[filtered_data["st_id2"] == stat_id][
            "st_id1"
        ].value_counts()

        # 1to2, 2to1 합치기
        combine_values = pd.concat([total_num_left, total_num_right], axis=1)
        combine_values.fillna((1), inplace=True)
        combine_values.rename(columns=dict(st_id2="1to2", st_id1="2to1"), inplace=True)

        # 계산 결과 종합
        result_concat = (
            combine_values.reset_index().groupby("index")[["1to2", "2to1"]].sum()
        )

        """
        역 주변 대여소로 특정할 경우 역과 관련된 따릉이 대여소는 제외하는 기능 추가
        """
        # 역 주변 대여소가 검색될 때 해당역 주변 대여소는 제거한다. | 316 대여소는 종각역과 관련됐는데, 종각과 관련된 대여소는 제거했다.
        try:
            # 지하철역 이름 검색
            filter_sub = near_sub.query("bi_st_id == @stat_id")["sub_name"].iloc[0]
            # 지하철역 이름이 포함된 자전거역 검색
            filter_sub_2 = near_sub.query("sub_name ==@filter_sub")["bi_st_id"].values
            # 관련 내용 제거
            result_concat = result_concat[~result_concat.index.isin(filter_sub_2)]
        except:
            pass

        """
        총 이동횟수를 구한 뒤 50회 미만인 대여소는 이동량이 없다고 판단.
        """

        # 이동기록 기록 50건 이하 제거
        count_rent = 50
        result_concat = result_concat[
            (result_concat["1to2"] > count_rent) | (result_concat["2to1"] > count_rent)
        ]

        ### 지하철만 모은건데 전체 대여소를 설정하는게 더 좋다고 생각해서 아래와 같이 변경하였음.
        # 지하철역 인근 따릉이 대여소 정보와 종합
        # sorted_sub = pd.merge(
        #     result_concat,
        #     near_sub,
        #     how="left",
        #     left_on=result_concat.index,
        #     right_on="bi_st_id",
        # ).dropna(subset=["sub_name"])
        # self.asd= sorted_sub.copy()

        sorted_sub = pd.merge(
            result_concat,
            near_sub,
            how="left",
            left_on=result_concat.index,
            right_on="bi_st_id",
        ).sort_values(by=["1to2"], ascending=False)[:50]

        """
        대여소를 기준으로 다른 대여소와 거리 계산 
        """
        # 기준 대여소와 역근처 대여소 직선 거리계산
        station_lat_lon = station[station["st_id"].isin(sorted_sub["bi_st_id"])][
            ["st_id", "st_name", "latitude", "longtitude"]
        ]

        dist_to_station = haversine_np(
            station.loc[station["st_id"] == stat_id, "longtitude"].values,
            station.loc[station["st_id"] == stat_id, "latitude"].values,
            station_lat_lon["longtitude"].values,
            station_lat_lon["latitude"].values,
        )
        station_lat_lon["distance"] = dist_to_station

        #  해당 대여소와의 거리정보 종합
        sorted_sub = pd.merge(
            sorted_sub, station_lat_lon, left_on="bi_st_id", right_on="st_id"
        ).drop(columns=["st_id"])

        """
        연산 속도를 줄이기 위해 top num개 대여소만 선정
        """
        sorted_sub["total"] = sorted_sub["1to2"] + sorted_sub["2to1"]
        sorted_sub = sorted_sub.sort_values(by="total", ascending=False)[
            :num
        ]  #####################
        self.test_val = sorted_sub

        """
        가는 시간 및 거리 계산
        """
        # 대여소별 예상 도착시간 계산

        result_station = []
        for j in sorted_sub["bi_st_id"]:
            BM = filtered_data["st_id2"] == j
            st_id1_time = (
                filtered_data[BM]["riding_time"]
                .value_counts()
                .sort_values(ascending=False)
            )
            BM = filtered_data["st_id1"] == j
            st_id2_time = (
                filtered_data[BM]["riding_time"]
                .value_counts()
                .sort_values(ascending=False)
            )

            ### 1to2 걸린시간 + 2to1 걸린시간 합
            all_rent = st_id1_time.add(st_id2_time, fill_value=0)

            ### 1to2 & 2to1 대여기록 합
            total_record = all_rent.sum()

            k = []
            i = 2
            ### 기록 많은 순만 종합
            while len(k) < 1:
                k = all_rent[all_rent >= (total_record / i)]
                i = i * 1.5

            ### 대여시간
            ind = k.index
            ### 대여기록
            val = k.values
            ### 대여기록 합
            a = k.sum()
            ### 대여시간 * 대여기록
            asddd = sum([a * b for a, b in zip(ind, val)])
            # 평균 시간
            ddddd = asddd / a

            # 올림
            result = round(ddddd, 0)
            result_station.append(result)

        # 예상시간정보 종합(대여소: 대여소에서 출발)
        est_time = pd.DataFrame(result_station, columns=["대여소"])

        # return 자료 생성
        self.nearest_sub = pd.concat(
            [sorted_sub.reset_index(drop=True), est_time], axis=1
        )

        b = self.nearest_sub.sub_name.isna()

        var = np.where(b == True, "자주가는 대여소", "자주가는 지하철역")

        self.nearest_sub["color"] = var

    def table_info(self, num=20):

        # 대여소 예상시간 테이블 만들기
        nearest_sub_sorted = (
            (self.nearest_sub[["sub_name", "대여소"]])
            .dropna(subset="sub_name")
            .drop_duplicates(subset="sub_name")
        )
        nearest_sub_sorted.columns = ["역이름", "예상시간"]

        nearest_sub_sorted["예상시간"] = nearest_sub_sorted["예상시간"].apply(
            lambda x: str(int(x)) + "분"
        )

        return nearest_sub_sorted[:num]

    def frequent_estimation(self, num=20):
        data = self.nearest_sub.query('color == "자주가는 대여소"')[:num]
        data_index = data.bi_st_id.to_list()
        est_time = data[["st_name", "대여소"]]
        est_time.columns = ["대여소 이름", "예상시간"]
        est_time["예상시간"] = est_time["예상시간"].apply(lambda x: str(int(x)) + "분")
        return est_time

        ## 혹시몰라 백업용
        # labels = self.bike_info.query("value == @data_index")
        # est_time = data[["대여소", "bi_st_id", "total"]]
        # result = pd.merge(
        #     labels, est_time, how="left", left_on="value", right_on="bi_st_id"
        # ).sort_values(by="total", ascending=False)
        # return result[["label", "대여소"]]

    def plotly_image(self):

        # figure 만들기P
        fig = px.scatter_mapbox(
            self.nearest_sub,
            lat="latitude",
            lon="longtitude",
            # hover_data={'latitude':False,'longtitude':False,'st_name':True},
            opacity=0.8,
            # size='total', size_max=20,
            zoom=14,
            custom_data=["st_name", "대여소", "total", "distance"],
            color="color",
            color_discrete_sequence=["#35C768", "#3581C7"],  # 대여소 # 자하철
        )
        # marker 정보
        # fig.for_each_trace(lambda t: t.update(name="<b>" + t.name + "</b>"))
        fig.update_traces(
            marker={"size": 10},
            hovertemplate="대여소 : %{customdata[0]} <br>예상시간 : %{customdata[1]}분 <br>대여기록 : %{customdata[2]}건",
        )
        main_lat = self.station.query("st_id==@self.stat_id")["latitude"]
        main_long = self.station.query("st_id==@self.stat_id")["longtitude"]
        print(main_long)
        # 해당 따릉이 대여소 색 표시
        fig_2 = go.Figure(
            go.Scattermapbox(
                lat=main_lat,
                lon=main_long,
                mode="markers",
                marker={"size": 40, "color": "#CA1B1B", "opacity": 0.2},
                showlegend=False,
            )
        )
        fig_2.update_traces(hoverinfo="skip")
        fig.add_trace(fig_2.data[0])

        # 해당 따릉이 대여소 둘레 표시
        fig_3 = go.Figure(
            go.Scattermapbox(
                name="",
                lat=main_lat,
                lon=main_long,
                mode="markers",
                marker={"size": 12, "color": "#FF1B1B", "opacity": 0.9},
                text=self.bike_info.query("value==@self.stat_id")["label"].values,
                hovertemplate="%{text}",
                showlegend=False,
                # zoom=14
                # text=self.station.query("st_id==@self.stat_id")["st_name"].values,
            )
        )
        # fig_3.update_traces(hoverinfo='skip',hovertemplate=None)
        fig.add_trace(fig_3.data[0])

        # 지도 정보 업데이트
        # fig.update_traces(hoverinfo='skip',hovertemplate=None)
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            mapbox_zoom=14,
            mapbox_center={"lat": main_lat.iloc[0], "lon": main_long.iloc[0]},
            mapbox=dict(
                accesstoken="pk.eyJ1IjoieWFuZ29vcyIsImEiOiJjbDNqd2tkN2IwbGdmM2pvNzF0c2M4NnZkIn0.J3IjPYg3w28cGiWkUD7bnA",
                style="mapbox://styles/yangoos/cl4cljdka001o14n3cll7whrh/draft",
            ),
            legend=dict(
                yanchor="top",
                y=0.82,
                xanchor="right",
                x=0.95,
                bgcolor="rgba(223, 235, 223, 0.8)",
                title={"text": None},
            ),
        )
        # fig.show()
        off_plot = plotly.io.to_html(
            fig,
            config=dict(displayModeBar=False),
            include_plotlyjs=False,
            full_html=True,
            include_mathjax=False,
        )
        bs = BeautifulSoup(off_plot, features="html.parser")
        div_data = bs.find("div", "plotly-graph-div")
        script_data = bs.find("script").text.replace(" ", "")
        context = {"div_data": str(div_data), "script_data": str(script_data)}
        return context
