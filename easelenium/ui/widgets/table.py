from easelenium.ui.generator.page_object_class import get_by_as_code_str
from wx.grid import Grid


class Table(Grid):
    def __init__(self, parent):
        Grid.__init__(self, parent)

        self.selected_row = None
        self.__data = None
        self.__data_attrs = [u"name", "by", "selector", "location", "dimensions"]

    def get_selected_data(self):
        return (
            self.__data[self.selected_row]
            if self.selected_row is not None
            else self.selected_row
        )

    def load_data(self, data):
        self.clear_table()

        self.__data = data
        count = len(self.__data)

        if not self.GetTable():
            self.CreateGrid(count, len(self.__data_attrs))
            table = self.GetTable()
        else:
            table = self.GetTable()
            table.AppendRows(count)
            table.AppendCols(len(self.__data_attrs))

        # filling headers
        for attr in self.__data_attrs:
            table.SetColLabelValue(self.__data_attrs.index(attr), attr.capitalize())

        # filling data
        for d in self.__data:
            j = self.__data.index(d)
            for attr in self.__data_attrs:
                value = getattr(d, attr)
                i = self.__data_attrs.index(attr)
                is_by = attr == self.__data_attrs[1]
                is_location_or_dimensions = type(value) in (tuple, list)
                if is_by:
                    value = get_by_as_code_str(value)
                elif is_location_or_dimensions:
                    value = str(value)

                table.SetValue(j, i, value)

        self.AutoSizeColumns()

    def clear_table(self):
        self.ClearGrid()

    def select_row(self, row):
        if row:
            self.selected_row = row
            self.SelectRow(row)
            self.Scroll(0, row)
