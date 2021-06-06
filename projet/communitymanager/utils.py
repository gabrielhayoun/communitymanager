from datetime import datetime, timedelta
from calendar import HTMLCalendar, _localized_month, month_name, day_name, day_abbr
from .models import Post


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, posts):
        events_per_day = posts.filter(date_event__day=day)
        d = ''
        for event in events_per_day:
            d += f'<a  href="/post/{event.id}"><li class="{event.priority}" >{event.title}</li></a>'

        if day != 0:
            return f"<td><span class='date'>{day}</span><ul class='calendarul'> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, posts):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, posts)
        return f'<tr> {week} </tr>'

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = ''.join(self.formatweekday(i) for i in self.iterweekdays())
        return '<tr class="days">%s</tr>' % s

    # formats a month as a table
    def formatmonth(self, posts, withyear=True,):
        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, posts)}\n'
        return cal



    def formatmonthname_week(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (month_name[themonth], theyear)
        else:
            s = '%s' % month_name[themonth]
        return '<tr><th colspan="8" class="%s">%s</th></tr>' % (
            self.cssclass_month_head, s)

    def formatweekday_week(self, day, number, width):
        """
        Returns a formatted week day name.
        """
        if width >= 9:
            names = day_name
        else:
            names = day_abbr
        if number != 0:
            return names[day][:width].center(width) + " " + str(number)
        else:
            return names[day][:width].center(width)

    def formathour(self, day, hour, posts):
        events_per_day = posts.filter(date_event__day=day, date_event__hour=hour)
        d = ''
        for event in events_per_day:
            d += f'<a  href="/post/{event.id}"><li class="{event.priority}" >{event.title}</li></a>'
        if day != 0:
            return f"<td class='tdhour'><ul> {d} </ul></td>"
        return '<td></td>'

    def formatweekhour(self, theweek, hour,  posts):
        week = ''
        for d, weekday in theweek:
                week += self.formathour(d, hour, posts)
        return f'<tr><td class="dayshourtd">{hour}:00</td>{week}</tr>'

    def formatweektable(self, theweek, posts):

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendarhour" >\n'
        cal += f'{self.formatmonthname_week(self.year, self.month, withyear=True)}\n'
        s=""
        for i, number in theweek:
            s +=f"<td class='dayshourtd'>{self.formatweekday_week(number, i, 3)}"
        cal += f'<tr class="dayshourtr"><td class="dayshourtd">hour</td>{s}</tr>\n'
        for hour in range(0, 24):
            cal += f'{self.formatweekhour(theweek, hour,  posts)}\n'
        return cal