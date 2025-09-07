from datetime import datetime, timedelta

def get_date_range(time_filter: str) -> tuple[datetime, datetime]:
    current_date = datetime.now()
    current_date_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if time_filter == "past":
        return datetime.min, current_date
    elif time_filter == "future":
        return current_date, datetime.max
    elif time_filter == "today":
        today_end = current_date_start + timedelta(days=1) - timedelta(microseconds=1)
        return current_date_start, today_end
    elif time_filter == "this_week":
        days_since_monday = current_date.weekday()
        week_start = current_date_start - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=7) - timedelta(microseconds=1)
        return week_start, week_end
    elif time_filter == "this_month":
        month_start = current_date_start.replace(day=1)
        if current_date_start.month == 12:
            month_end = month_start.replace(year=current_date_start.year + 1, month=1) - timedelta(microseconds=1)
        else:
            month_end = month_start.replace(month=current_date_start.month + 1) - timedelta(microseconds=1)
        return month_start, month_end
    elif time_filter == "next_week":
        days_until_next_monday = 7 - current_date.weekday()
        next_week_start = current_date_start + timedelta(days=days_until_next_monday)
        next_week_end = next_week_start + timedelta(days=7) - timedelta(microseconds=1)
        return next_week_start, next_week_end
    elif time_filter == "next_month":
        if current_date_start.month == 12:
            next_month_start = current_date_start.replace(year=current_date_start.year + 1, month=1, day=1)
            next_month_end = next_month_start.replace(month=2) - timedelta(microseconds=1)
        else:
            next_month_start = current_date_start.replace(month=current_date_start.month + 1, day=1)
            if current_date_start.month == 11:
                next_month_end = next_month_start.replace(year=current_date_start.year + 1, month=1) - timedelta(microseconds=1)
            else:
                next_month_end = next_month_start.replace(month=current_date_start.month + 2) - timedelta(microseconds=1)
        return next_month_start, next_month_end
    
    return None, None

def is_weekend(date_str: str) -> str:
    """Check if date is weekend"""
    weekend_or_not = datetime.strptime(date_str, "%d/%m/%Y").strftime("%A") in ["Saturday", "Sunday"]
    if weekend_or_not:
        return "weekend"
    else:
        return "workday"