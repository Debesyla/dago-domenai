"""
Profile loader with dependency resolution.

v0.10 - Composable Profile System

This module handles loading profiles, resolving dependencies, and
validating profile combinations. It implements topological sorting
to ensure profiles are executed in the correct order.
"""

from typing import List, Set, Dict, Optional, Tuple
from collections import deque

from .profile_schema import (
    validate_profile_name,
    get_profile_dependencies,
    is_core_profile,
    is_meta_profile,
    get_all_profiles,
    get_core_profiles,
    get_meta_profiles,
    get_profile_info,
    PROFILE_DEPENDENCIES,
    PROFILE_METADATA,
)


class ProfileError(Exception):
    """Base exception for profile-related errors."""
    pass


class UnknownProfileError(ProfileError):
    """Raised when an unknown profile is requested."""
    pass


class CircularDependencyError(ProfileError):
    """Raised when profiles have circular dependencies."""
    pass


def load_profile(profile_name: str) -> Dict:
    """
    Load a single profile with its metadata.
    
    Args:
        profile_name: Name of the profile to load
        
    Returns:
        Profile information dictionary
        
    Raises:
        UnknownProfileError: If profile doesn't exist
    """
    if not validate_profile_name(profile_name):
        raise UnknownProfileError(f"Unknown profile: {profile_name}")
    
    info = get_profile_info(profile_name)
    if not info:
        raise UnknownProfileError(f"Profile metadata not found: {profile_name}")
    
    return {
        'name': profile_name,
        'category': info.get('category').value if info.get('category') else None,
        'description': info.get('description', ''),
        'dependencies': get_profile_dependencies(profile_name),
        'metadata': info,
    }


def expand_meta_profiles(profiles: List[str]) -> List[str]:
    """
    Expand meta profiles to their constituent profiles.
    
    Meta profiles like 'standard' expand to multiple individual profiles.
    This function recursively expands all meta profiles.
    
    Args:
        profiles: List of profile names (may include meta profiles)
        
    Returns:
        List of expanded profile names (no meta profiles)
        
    Example:
        expand_meta_profiles(['standard', 'dns'])
        -> ['whois', 'dns', 'http', 'ssl', 'seo']
    """
    expanded = set()
    
    for profile in profiles:
        if not validate_profile_name(profile):
            raise UnknownProfileError(f"Unknown profile: {profile}")
        
        if is_meta_profile(profile):
            # Recursively expand meta profile
            deps = get_profile_dependencies(profile)
            sub_expanded = expand_meta_profiles(deps)
            expanded.update(sub_expanded)
        else:
            expanded.add(profile)
    
    return list(expanded)


def resolve_profile_dependencies(profiles: List[str]) -> List[str]:
    """
    Resolve profile dependencies and return execution order.
    
    This function:
    1. Expands meta profiles
    2. Collects all dependencies
    3. Performs topological sort to determine execution order
    4. Returns profiles in dependency order (dependencies first)
    
    Args:
        profiles: List of requested profile names
        
    Returns:
        Ordered list of profiles to execute (dependencies first)
        
    Raises:
        UnknownProfileError: If any profile is unknown
        CircularDependencyError: If circular dependencies detected
        
    Example:
        resolve_profile_dependencies(['seo', 'headers'])
        -> ['http', 'content', 'headers', 'seo']
        # http is first (no deps), content depends on http, etc.
    """
    # Expand meta profiles
    expanded = expand_meta_profiles(profiles)
    
    # Collect all profiles including dependencies
    all_profiles = set(expanded)
    queue = deque(expanded)
    
    while queue:
        profile = queue.popleft()
        deps = get_profile_dependencies(profile)
        
        for dep in deps:
            if dep not in all_profiles:
                all_profiles.add(dep)
                queue.append(dep)
    
    # Topological sort using Kahn's algorithm
    # Build in-degree map
    in_degree = {p: 0 for p in all_profiles}
    adj_list = {p: [] for p in all_profiles}
    
    for profile in all_profiles:
        deps = get_profile_dependencies(profile)
        for dep in deps:
            adj_list[dep].append(profile)
            in_degree[profile] += 1
    
    # Start with profiles that have no dependencies
    queue = deque([p for p in all_profiles if in_degree[p] == 0])
    sorted_profiles = []
    
    while queue:
        profile = queue.popleft()
        sorted_profiles.append(profile)
        
        # Reduce in-degree for dependent profiles
        for dependent in adj_list[profile]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)
    
    # Check for circular dependencies
    if len(sorted_profiles) != len(all_profiles):
        missing = all_profiles - set(sorted_profiles)
        raise CircularDependencyError(
            f"Circular dependency detected involving: {', '.join(missing)}"
        )
    
    return sorted_profiles


def parse_profile_string(profile_str: str) -> List[str]:
    """
    Parse a comma-separated profile string into list.
    
    Args:
        profile_str: Comma-separated profile names (e.g., "dns,ssl,http")
        
    Returns:
        List of profile names
        
    Example:
        parse_profile_string("dns, ssl, http")
        -> ['dns', 'ssl', 'http']
    """
    if not profile_str or not profile_str.strip():
        return []
    
    return [p.strip() for p in profile_str.split(',') if p.strip()]


def get_available_profiles() -> Dict[str, List[str]]:
    """
    Get all available profiles organized by category.
    
    Returns:
        Dictionary mapping category names to lists of profile names
        
    Example:
        {
            'core': ['whois', 'dns', 'http', 'ssl'],
            'analysis': ['headers', 'content', 'infrastructure', 'technology', 'seo'],
            'intelligence': ['security', 'compliance', 'business', 'language', ...],
            'meta': ['quick-check', 'standard', 'complete', ...]
        }
    """
    categories = {
        'core': [],
        'analysis': [],
        'intelligence': [],
        'meta': [],
    }
    
    for profile in get_all_profiles():
        info = get_profile_info(profile)
        if info:
            category = info.get('category')
            if category:
                category_name = category.value
                if category_name in categories:
                    categories[category_name].append(profile)
    
    return categories


def validate_profile_combination(profiles: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that a profile combination is valid.
    
    Checks:
    - All profiles exist
    - No circular dependencies
    - Can be resolved to execution order
    
    Args:
        profiles: List of profile names
        
    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "error description")
    """
    if not profiles:
        return False, "No profiles specified"
    
    # Check if all profiles exist
    for profile in profiles:
        if not validate_profile_name(profile):
            return False, f"Unknown profile: {profile}"
    
    # Try to resolve dependencies
    try:
        resolve_profile_dependencies(profiles)
        return True, None
    except ProfileError as e:
        return False, str(e)


def get_profile_execution_plan(profiles: List[str]) -> Dict:
    """
    Get detailed execution plan for a set of profiles.
    
    Returns information about:
    - Execution order
    - Core vs analysis profiles
    - Parallelization opportunities
    - Estimated duration
    
    Args:
        profiles: List of requested profile names
        
    Returns:
        Dictionary with execution plan details
        
    Example:
        {
            'requested': ['seo', 'headers'],
            'expanded': ['http', 'content', 'headers', 'seo'],
            'execution_order': ['http', 'content', 'headers', 'seo'],
            'core_profiles': ['http'],
            'analysis_profiles': ['content', 'headers', 'seo'],
            'parallel_groups': [
                ['http'],  # Group 1: Core profiles (can run in parallel)
                ['content'],  # Group 2: Depends on http
                ['headers', 'seo']  # Group 3: Can run in parallel
            ],
            'estimated_duration': '2-5s'
        }
    """
    # Resolve to execution order
    execution_order = resolve_profile_dependencies(profiles)
    
    # Categorize profiles
    core = [p for p in execution_order if is_core_profile(p)]
    analysis = [p for p in execution_order if not is_core_profile(p) and not is_meta_profile(p)]
    
    # Build parallel groups based on dependencies
    parallel_groups = []
    remaining = set(execution_order)
    satisfied = set()
    
    while remaining:
        # Find profiles whose dependencies are satisfied
        can_run = []
        for profile in remaining:
            deps = get_profile_dependencies(profile)
            if all(dep in satisfied for dep in deps):
                can_run.append(profile)
        
        if not can_run:
            break  # Shouldn't happen if topological sort worked
        
        parallel_groups.append(can_run)
        satisfied.update(can_run)
        remaining -= set(can_run)
    
    # Estimate duration
    from .profile_schema import estimate_duration
    duration = estimate_duration(execution_order)
    
    return {
        'requested': profiles,
        'expanded': expand_meta_profiles(profiles),
        'execution_order': execution_order,
        'core_profiles': core,
        'analysis_profiles': analysis,
        'parallel_groups': parallel_groups,
        'estimated_duration': duration,
        'total_profiles': len(execution_order),
    }


def suggest_profile_for_use_case(use_case: str) -> List[str]:
    """
    Suggest profiles for common use cases.
    
    Args:
        use_case: Use case description (e.g., "quick", "security", "seo")
        
    Returns:
        List of recommended profile names
    """
    use_case_lower = use_case.lower()
    
    suggestions = {
        'quick': ['quick-check'],
        'fast': ['quick-check'],
        'filter': ['quick-check'],
        'standard': ['standard'],
        'normal': ['standard'],
        'default': ['standard'],
        'security': ['technical-audit'],
        'audit': ['technical-audit'],
        'technical': ['technical-audit'],
        'business': ['business-research'],
        'research': ['business-research'],
        'market': ['business-research'],
        'seo': ['standard'],  # Includes seo profile
        'complete': ['complete'],
        'full': ['complete'],
        'everything': ['complete'],
        'monitor': ['monitor'],
        'tracking': ['monitor'],
        'changes': ['monitor'],
    }
    
    return suggestions.get(use_case_lower, ['standard'])
