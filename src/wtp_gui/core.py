"""Flet APP."""

import warnings

import flet as ft
import matplotlib as mpl
import matplotx as mpx
import welltestpy as wtp
from flet.matplotlib_chart import MatplotlibChart

mpl.use("svg")
style = mpx.styles.solarized["dark"]


def main(page: ft.Page):
    """Set up main flet APP."""
    def on_tab_change(e):
        # not really working (sometimes newly created tab not selected)
        if e.control.selected_index == len(tabs_view.tabs) - 1:
            pick_files(e)

    def on_tab_close(e):
        close_index = e.control.data
        selected = tabs_view.selected_index
        # print(f"{close_index=}, {selected=}")
        tabs_view.tabs.pop(close_index)
        if close_index <= selected:
            # print("close_index <= selected")
            tabs_view.selected_index = max(selected - 1, 0)
        # print(f"{tabs_view.selected_index=}")
        update_tabs()
        page.update()

    def on_tile_change(e):
        cmp, test, loaded = e.control.data
        if not loaded:
            e.control.controls.append(ft.Container(ft.ProgressRing(), padding=50))
            page.update()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fig_test = cmp.plot(select_tests=[test], style=style, title=False)
            mpl_test = MatplotlibChart(figure=fig_test, isolated=True, transparent=True)
            mpl_test.width = 800
            e.control.controls[0] = mpl_test
            e.control.data[2] = True  # is now loaded
            page.update()

    def update_tabs():
        for i, tab in enumerate(tabs_view.tabs[:-1]):
            tab.tab_content.controls[2].data = i  # close button data holds tab id

    def add_cmp(path):
        cmp = wtp.load_campaign(path)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig = cmp.plot_wells(style=style).get_figure()
        mpl = MatplotlibChart(figure=fig, isolated=True, transparent=True)
        mpl.width = 800
        cmp_tile = ft.ExpansionTile(
            title=ft.Text(cmp.name),
            subtitle=ft.Text(str(cmp)),
            affinity=ft.TileAffinity.LEADING,
            leading=ft.Icon(ft.icons.INSERT_CHART_OUTLINED_OUTLINED),
            maintain_state=True,
            initially_expanded=True,
            controls=[mpl],
        )

        test_tiles = [cmp_tile]
        for test in sorted(cmp.tests):
            tile_test = ft.ExpansionTile(
                title=ft.Text(cmp.tests[test].name),
                subtitle=ft.Text(str(cmp.tests[test])),
                affinity=ft.TileAffinity.TRAILING,
                leading=ft.Icon(ft.icons.SCATTER_PLOT),
                maintain_state=True,
                initially_expanded=False,
                controls=[],
                data=[cmp, test, False],
                on_change=on_tile_change,
            )
            test_tiles.append(tile_test)

        tab_idx = len(tabs_view.tabs) - 1
        tab = ft.Tab(
            tab_content=ft.Row(
                [
                    ft.Icon(ft.icons.INSERT_CHART_OUTLINED_OUTLINED),
                    ft.Text(cmp.name),
                    ft.IconButton(ft.icons.CLOSE, on_click=on_tab_close, data=tab_idx),
                ]
            ),
            content=ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            controls=test_tiles,
                            scroll=ft.ScrollMode.AUTO,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            width=1000,
                        ),
                        padding=ft.Padding(top=20, bottom=0, left=0, right=0),
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
        )
        tab.data = cmp
        tabs_view.tabs.insert(-1, tab)
        tabs_view.selected_index = tab_idx
        tabs_view.update()

    def pick_files(_):
        return pick_files_dialog.pick_files(allow_multiple=True)

    def pick_files_result(e: ft.FilePickerResultEvent):
        if e.files is not None:
            page.snack_bar.open = True
            page.update()
            for file in e.files:
                add_cmp(file.path)
            page.snack_bar.open = False
            page.update()

    def show_bs(_):
        bs.open = True
        bs.update()

    def close_bs(_):
        bs.open = False
        bs.update()

    add_tab = ft.Tab(
        tab_content=ft.IconButton(ft.icons.ADD, on_click=pick_files),
        content=ft.Container(
            ft.Text("Load a new campaign by pressing the + button."),
            alignment=ft.alignment.center,
            expand=True,
        ),
    )
    tabs_view = ft.Tabs(animation_duration=300, tabs=[add_tab], expand=True)
    # , on_change=on_tab_change)
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    bs = ft.BottomSheet(
        ft.Container(
            ft.Column(
                [
                    ft.Text("welltestpy GUI"),
                    ft.Text("by Sebastian Müller"),
                    ft.ElevatedButton("Close", on_click=close_bs),
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=10,
        ),
        open=False,
    )
    sb = ft.SnackBar(ft.Container(ft.ProgressBar()), bgcolor=ft.colors.BACKGROUND)

    page.overlay.append(pick_files_dialog)
    page.overlay.append(bs)
    page.snack_bar = sb
    page.snack_bar.open = False

    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.PAGES),
        leading_width=40,
        title=ft.Text("welltestpy GUI", font_family="Courier New"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(ft.icons.FILE_OPEN, on_click=pick_files),
            # ft.IconButton(ft.icons.SETTINGS),
            ft.IconButton(ft.icons.HELP, on_click=show_bs),
        ],
    )

    page.add(tabs_view)


def gui():
    """Welltestpy GUI."""
    ft.app(target=main)


if __name__ == "__main__":
    gui()
