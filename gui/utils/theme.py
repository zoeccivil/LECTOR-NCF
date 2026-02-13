"""
Theme constants and design system for LECTOR-NCF GUI
"""

# Color Palette - Modern Minimalist Design
COLORS = {
    # Primary Colors
    'PRIMARY': '#2563EB',           # Modern blue
    'PRIMARY_DARK': '#1E40AF',      # Darker blue
    'PRIMARY_LIGHT': '#DBEAFE',     # Light blue background
    
    # Status Colors
    'SUCCESS': '#10B981',            # Emerald green
    'WARNING': '#F59E0B',            # Amber
    'ERROR': '#EF4444',              # Soft red
    'PENDING': '#F59E0B',            # Amber (same as warning)
    
    # Gray Scale
    'GRAY_50': '#F9FAFB',
    'GRAY_100': '#F3F4F6',
    'GRAY_200': '#E5E7EB',
    'GRAY_300': '#D1D5DB',
    'GRAY_700': '#374151',
    'GRAY_900': '#111827',
    
    # Base Colors
    'WHITE': '#FFFFFF',
    'BLACK': '#000000',
}

# Typography
FONTS = {
    'FAMILY': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    'SIZE_CAPTION': '11px',
    'SIZE_BODY': '13px',
    'SIZE_SUBTITLE': '15px',
    'SIZE_TITLE': '20px',
    'SIZE_HEADING': '28px',
    'WEIGHT_REGULAR': 400,
    'WEIGHT_MEDIUM': 500,
    'WEIGHT_SEMIBOLD': 600,
    'WEIGHT_BOLD': 700,
}

# Spacing (in pixels)
SPACING = {
    'XS': 4,
    'SM': 8,
    'MD': 12,
    'LG': 16,
    'XL': 24,
    'XXL': 32,
}

# Border Radius
RADIUS = {
    'SMALL': '6px',
    'MEDIUM': '8px',
    'LARGE': '12px',
}

# Shadows
SHADOWS = {
    'SMALL': '0 1px 3px rgba(0,0,0,0.1)',
    'MEDIUM': '0 4px 6px rgba(0,0,0,0.1)',
    'LARGE': '0 10px 15px rgba(0,0,0,0.1)',
}

# Layout
LAYOUT = {
    'SIDEBAR_WIDTH': 220,
    'HEADER_HEIGHT': 60,
    'TABLE_ROW_HEIGHT': 48,
}

# Status Colors Mapping
STATUS_COLORS = {
    'pendiente': COLORS['PENDING'],
    'revisada': COLORS['SUCCESS'],
    'exportada': COLORS['GRAY_700'],
}

# Icon Sizes
ICON_SIZES = {
    'SMALL': 16,
    'MEDIUM': 24,
    'LARGE': 32,
}
