"""Utilities for reading markdown files in different contexts."""

import os
import logging
from pathlib import Path
from typing import Optional

_LOGGER = logging.getLogger(__name__)


def read_md_template(filename: str, is_ha_mode: bool = False) -> str:
    """
    Read a markdown template file from the appropriate location.
    
    Args:
        filename: Name of the markdown file (e.g., "request_action_prompt.md")
        is_ha_mode: If True, reads from HA context path, otherwise from CLI context
        
    Returns:
        Content of the markdown file
        
    Raises:
        FileNotFoundError: If the file cannot be found
        IOError: If the file cannot be read
    """
    if is_ha_mode:
        # Home Assistant context: core/prompts/filename
        base_path = Path(__file__).parent.parent  # Go up from utils to core
        template_path = base_path / "prompts" / filename
    else:
        # CLI context: custom_components/neural/core/prompts/filename
        base_path = Path(__file__).parent.parent.parent  # Go up from utils to neural
        template_path = base_path / "core" / "prompts" / filename
    
    _LOGGER.debug("Reading template from: %s", template_path)
    
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()
        _LOGGER.debug("Successfully read template: %s (%d characters)", filename, len(content))
        return content
    except FileNotFoundError:
        _LOGGER.error("Template file not found: %s", template_path)
        raise FileNotFoundError(f"Template file not found: {template_path}")
    except IOError as e:
        _LOGGER.error("Error reading template file %s: %s", template_path, e)
        raise IOError(f"Error reading template file {template_path}: {e}")


def get_template_path(filename: str, is_ha_mode: bool = False) -> str:
    """
    Get the full path to a template file without reading it.
    
    Args:
        filename: Name of the markdown file
        is_ha_mode: If True, returns HA context path, otherwise CLI context
        
    Returns:
        Full path to the template file
    """
    if is_ha_mode:
        base_path = Path(__file__).parent.parent
        template_path = base_path / "prompts" / filename
    else:
        base_path = Path(__file__).parent.parent.parent
        template_path = base_path / "core" / "prompts" / filename
    
    return str(template_path)


def list_available_templates(is_ha_mode: bool = False) -> list[str]:
    """
    List all available markdown templates.
    
    Args:
        is_ha_mode: If True, lists from HA context, otherwise CLI context
        
    Returns:
        List of available template filenames
    """
    if is_ha_mode:
        base_path = Path(__file__).parent.parent / "prompts"
    else:
        base_path = Path(__file__).parent.parent.parent / "core" / "prompts"
    
    if not base_path.exists():
        _LOGGER.warning("Templates directory not found: %s", base_path)
        return []
    
    templates = []
    for file_path in base_path.glob("*.md"):
        templates.append(file_path.name)
    
    _LOGGER.debug("Found %d templates: %s", len(templates), templates)
    return templates
