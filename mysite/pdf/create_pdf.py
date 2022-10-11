from Process.create_dashboards import Processing
from fpdf import FPDF
import sys

abs_path_static = "C:\\Users\\maksi\\Desktop\\Python\\Diploma\\mysite\\pdf"


class MyPDF:

    def __init__(self):
        self.pdf = FPDF()

        self.WIDTH = 210
        self.HEIGHT = 297

        self.process = Processing()

    def _setFontVal(self, x, y, payload, font=10, is_value=False, value_payload="Ass", correcting_value=18):
        # self.pdf.ln(10)
        self.pdf.set_font('Arial', "", font)

        self.pdf.set_xy(x, y)
        self.pdf.cell(0, 0, str(payload))

        if is_value:
            self.pdf.set_font('Arial', "", 10)
            self.pdf.set_xy(x - correcting_value, y + 11)
            self.pdf.cell(0, 0, str(value_payload))

    # def _setFontValueOfPlot(self, x, y):
    #     self.pdf.ln(10)
    #     self.pdf.set_font('Arial', "", 40)
    #     self.pdf.set_xy(x, y)

    def _automatizationOfPdf(self, function, picture_name, payload_for_plot, payload_for_value, correcting_value=18,
                             x_picture=5, y_picture=30, x_value=185, period="week", folder="weekly", measure="day",
                             correct_loc_name_of_plot=15):

        plot, value = function(period=period)
        plot.savefig(abs_path_static + f"\\{folder}\\{picture_name}", dpi=100)

        self.pdf.image(f"./{folder}/{picture_name}", x_picture, y_picture, self.WIDTH / 2 - 10)
        self._setFontVal(x_picture + correct_loc_name_of_plot, y_picture + 75, payload=payload_for_plot)

        self._setFontVal(x_value, y_picture + 40, font=40, payload=value,
                         is_value=True, value_payload=payload_for_value,correcting_value=correcting_value)

    def createPDF(self, period="week", folder="weekly", measure="day"):
        self.pdf.add_page()

        self.pdf.set_font('Arial', 'B', 16)
        self.pdf.cell(0, 10, 'Weekly Website Visits Report', align='C')

        # Actions per Visit
        # amount_of_actions_per_visit, plt_amount_of_actions_per_visit = self.process.actionsPerVisit(period=period,
        #                                                                                             purpose="count-sum")
        # plt_amount_of_actions_per_visit.savefig(abs_path_static + f"\\{folder}\\actionsPerVisit.png", dpi=100)
        # self.pdf.image("./weekly/actionsPerVisit.png", 5, 30, self.WIDTH / 2 - 5)
        #
        # self._setFontVal(20, 110, payload=f'Sum of actions per {measure} throughout the {period}')
        #
        # self._setFontVal(self.WIDTH - (self.WIDTH / 4) - 15, 70, font=40, payload=amount_of_actions_per_visit,
        #                  is_value=True, value_payload=f"Overall Amount of Actions/{period}")

        # Count Sessions
        self._automatizationOfPdf(self.process.countSessions, "countSessions.png", x_picture=5, y_picture=20, x_value=150,
                                  period=period, folder=folder, measure=measure, correct_loc_name_of_plot=15,
                                  payload_for_plot=f'Sum of actions per {measure} throughout the {period}',
                                  payload_for_value=f"Overall Amount of Actions/{period}")

        # Average User Session
        self._automatizationOfPdf(self.process.averageUserSessionNew, "averageUserSession.png", x_picture=5, y_picture=108,
                                  x_value=130, period=period, folder=folder, measure=measure, correct_loc_name_of_plot=11,
                                  correcting_value=-2,
                                  payload_for_plot=f'Average user session per {measure} throughout the {period}',
                                  payload_for_value=f"Average user session/{period}")

        # Bounce Rate
        # plt_bounce_rate, bounce_rate = processing.bounceRate(period=period)
        # plt_bounce_rate.savefig(abs_path_static + f"\\{folder}\\bounceRate.png", dpi=100)

        self._automatizationOfPdf(self.process.bounceRate, "bounceRate.png", x_picture=5, y_picture=200,
                                  x_value=150, period=period, folder=folder, measure=measure, correct_loc_name_of_plot=11,
                                  correcting_value=6,
                                  payload_for_plot=f'Bounce rate per {measure} throughout the {period}',
                                  payload_for_value=f"Bounce rate/{period}")

        # Amount of Sessions

        self.pdf.output("test.pdf", "F")


if __name__ == "__main__":
    pdf = MyPDF()
    pdf.createPDF()
