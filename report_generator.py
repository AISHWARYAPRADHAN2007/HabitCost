from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def generate_pdf(df, currency, total_monthly, total_yearly, future_20, insights):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph("💸 HabitCost Financial Report", styles["Title"])
    )

    elements.append(Spacer(1, 20))


    # Summary

    elements.append(
        Paragraph("Financial Summary", styles["Heading2"])
    )

    summary = [
        ["Monthly Spending", f"{currency} {total_monthly:,.2f}"],
        ["Yearly Spending", f"{currency} {total_yearly:,.2f}"],
        ["20 Year Future Value", f"{currency} {future_20:,.2f}"]
    ]


    table = Table(summary)

    table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, None)
        ])
    )

    elements.append(table)

    elements.append(Spacer(1,20))


    # Habit Details

    elements.append(
        Paragraph("Habit Breakdown", styles["Heading2"])
    )


    habit_data = [
        [
            "Habit",
            "Category",
            "Monthly Cost",
            "Yearly Cost"
        ]
    ]


    for _, row in df.iterrows():

        habit_data.append(
            [
                row["Habit"],
                row["Category"],
                f"{currency} {row['Monthly Cost']:,.0f}",
                f"{currency} {row['Yearly Cost']:,.0f}"
            ]
        )


    habit_table = Table(habit_data)

    habit_table.setStyle(
        TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,None)
        ])
    )


    elements.append(habit_table)

    elements.append(Spacer(1,20))


    # Insights

    elements.append(
        Paragraph("Smart Insights", styles["Heading2"])
    )


    for insight in insights:

        elements.append(
            Paragraph("• " + insight, styles["BodyText"])
        )

        elements.append(Spacer(1,8))


    doc.build(elements)


    buffer.seek(0)

    return buffer