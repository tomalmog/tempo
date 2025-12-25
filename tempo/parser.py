"""Parse Claude Code output for rate limits and completion signals."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser
from dateutil import tz

from tempo.config import (
    COMPLETION_CODE,
    RATE_LIMIT_PATTERNS,
    RESET_TIME_PATTERN_WITH_TZ,
    RESET_TIME_PATTERN_NO_TZ,
)


@dataclass
class RateLimitInfo:
    """Information about a rate limit event."""
    
    reset_time: datetime
    timezone_name: str
    raw_message: str


@dataclass
class ParseResult:
    """Result of parsing Claude output."""
    
    is_complete: bool = False
    is_rate_limited: bool = False
    rate_limit_info: Optional[RateLimitInfo] = None


def detect_completion(output: str) -> bool:
    """Check if output contains the completion code."""
    return COMPLETION_CODE in output


def detect_rate_limit(output: str) -> bool:
    """Check if output indicates a rate limit."""
    output_lower = output.lower()
    return any(
        re.search(pattern, output_lower, re.IGNORECASE)
        for pattern in RATE_LIMIT_PATTERNS
    )


def parse_reset_time(output: str) -> Optional[RateLimitInfo]:
    """
    Extract reset time from rate limit message.
    
    Handles formats:
    - "resets 4am (America/Toronto)" - with explicit timezone
    - "resets 4am" - uses local timezone
    
    Returns: RateLimitInfo with parsed datetime in the correct timezone
    """
    # Try pattern with timezone first
    match = re.search(RESET_TIME_PATTERN_WITH_TZ, output, re.IGNORECASE)
    if match:
        time_str, timezone_name = match.groups()
    else:
        # Try pattern without timezone
        match = re.search(RESET_TIME_PATTERN_NO_TZ, output, re.IGNORECASE)
        if not match:
            return None
        time_str = match.group(1)
        timezone_name = "local"
    
    try:
        # Get the timezone
        if timezone_name == "local":
            timezone = tz.tzlocal()
        else:
            timezone = tz.gettz(timezone_name)
            if timezone is None:
                # Fallback to local timezone if we can't parse
                timezone = tz.tzlocal()
                timezone_name = "local"
        
        # Parse the time string
        # Handle formats like "4am", "4:30pm", "16:00"
        parsed_time = date_parser.parse(time_str)
        
        # Get current time in target timezone
        now = datetime.now(timezone)
        
        # Create reset datetime for today
        reset_dt = now.replace(
            hour=parsed_time.hour,
            minute=parsed_time.minute,
            second=0,
            microsecond=0,
        )
        
        # If reset time is in the past, it must be tomorrow
        if reset_dt <= now:
            from datetime import timedelta
            reset_dt = reset_dt + timedelta(days=1)
        
        return RateLimitInfo(
            reset_time=reset_dt,
            timezone_name=timezone_name,
            raw_message=output,
        )
    except (ValueError, AttributeError) as e:
        # If parsing fails, return None and let caller handle it
        return None


def parse_output(output: str) -> ParseResult:
    """
    Parse Claude output and determine state.
    
    Returns ParseResult indicating if task is complete or rate limited.
    """
    result = ParseResult()
    
    # Check for completion first
    if detect_completion(output):
        result.is_complete = True
        return result
    
    # Check for rate limit
    if detect_rate_limit(output):
        result.is_rate_limited = True
        result.rate_limit_info = parse_reset_time(output)
    
    return result

