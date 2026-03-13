"""Geometry Models - Complete Collection."""

__version__ = "1.0.0"

from .fisher_information import FisherInformationGeometry, create_fisher_geometry

__all__ = [
    'FisherInformationGeometry', 'create_fisher_geometry',
]
