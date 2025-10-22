"""Date utilities: thin wrappers around QuantLib calendars, adjustments, and conversions."""
from QuantLib import Date, Calendar, UnitedStates, TARGET, BusinessDayConvention, Period, Months, Days, DateParser
import datetime
from typing import Union
us_cal = UnitedStates()

def is_business_day(date: Date, calendar: Calendar = us_cal) -> bool:
    return calendar.isBusinessDay(date)

def advance_date(date: Date, n: int, unit: str = "Days", calendar: Calendar = us_cal, convention: BusinessDayConvention = BusinessDayConvention.Following) -> Date:
    """Advance a QuantLib Date by n units (Days, Months, or Years) using business day rules."""
    if unit == "Days":
        period = Period(n, Days)
    elif unit == "Months":
        period = Period(n, Months)
    else:
        raise ValueError("Unit must be 'Days' or 'Months'")
    return calendar.advance(date, period, convention)

def parse_date(date_str: str) -> Date:
    return DateParser.parseISO(date_str)
