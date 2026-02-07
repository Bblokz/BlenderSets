import bpy
from mathutils import kdtree

# ============================================================
# Auto–Fill Missing Weights From Nearest Vertex (Radius Aware)
# ============================================================
#
# WHAT THIS SCRIPT DOES
# ---------------------
# For the active mesh object:
#   1. It finds all vertices that are effectively "unweighted"
#      (no vertex groups OR all weights below a threshold).
#   2. For each such vertex, it looks for nearby vertices that
#      ARE properly weighted:
#        - If SEARCH_RADIUS <= 0.0:
#              use the globally nearest valid vertex.
#        - If SEARCH_RADIUS > 0.0:
#              collect all valid vertices inside that radius and
#              pick the one whose strongest weight (max group
#              weight) is highest (ties -> closest).
#   3. It copies all vertex-group weights from that chosen
#      source vertex onto the unweighted one.
#
# Vertices that already have sufficient total weight are left
# untouched.
#
# HOW TO USE
# ----------
# 1. Select your skinned mesh object (the one with vertex groups).
# 2. Make sure it is the active object.
# 3. Open a Text Editor in Blender, paste this script, and press
#    "Run Script".
# 4. (Optional) On Windows: Window → Toggle System Console to see
#    detailed debug prints.
# 5. After running, a small popup will show how many vertices
#    were fixed.
#
# TUNING TIPS
# -----------
# - WEIGHT_THRESHOLD:
#       Increase to treat more weak weights as "zero".
#       Decrease if you only want to fix totally empty vertices.
#
# - SEARCH_RADIUS:
#       0.0 or negative -> no limit (use global nearest).
#       positive       -> only look inside that radius; if some
#                         vertices stay unweighted, increase this.
#
# - N_DEBUG_PRINTS:
#       0   -> no per-vertex debug prints.
#       >0  -> print debug info for every N-th vertex that got fixed.
#
# ============================================================
# Settings
# ============================================================

# Below this value, weights are treated as "zero"/negligible.
# Typical useful values:
#   1e-4 (very tiny)
#   1e-3 or 5e-3 if you want to treat very faint weights as zero.
WEIGHT_THRESHOLD = 0.33

# If True, any existing groups on a "bad" vertex are removed
# before copying weights from the nearest valid vertex.
CLEAR_EXISTING_GROUPS = True

# If True, *only* vertices that have NO vertex groups at all
# are treated as "bad".
# If False (default), vertices where ALL group weights are below
# WEIGHT_THRESHOLD are also treated as bad.
ONLY_VERTICES_WITHOUT_GROUPS = False

# If True, process only the currently selected vertices
# (selection in Object or Edit mode; in Edit mode selection
# is synced when leaving Edit mode).
USE_SELECTED_VERTICES_ONLY = False

# Maximum distance to search for candidate source vertices.
# Units: Blender units in object space.
#   <= 0.0   : no limit, use global nearest vertex (original behavior).
#   > 0.0    : consider only vertices within this radius, then pick
#              the one with the highest max weight (ties -> closer).
SEARCH_RADIUS = 0.0

# Debug printing:
#   0  -> no per-vertex debug prints
#   n>0 -> print one debug line for every n vertices that were fixed
N_DEBUG_PRINTS = 0


# ============================================================
# Helper functions
# ============================================================

def get_vertex_weights(obj, vert_index):
    """
    Returns a list of (group_index, weight) for the given vertex.
    """
    vertex = obj.data.vertices[vert_index]
    result = []
    for group_element in vertex.groups:
        result.append((group_element.group, group_element.weight))
    return result


def is_unweighted_vertex(obj, vert_index, weight_threshold, only_without_groups):
    """
    Returns True if this vertex should be treated as "bad":
      - If only_without_groups is True:
            vertex.groups must be empty.
      - Else:
            vertex.groups is empty OR
            all weights are below the given threshold.
    """
    vertex = obj.data.vertices[vert_index]

    if not vertex.groups:
        # No groups at all -> always considered unweighted
        return True

    if only_without_groups:
        # We only treat "no groups at all" as bad
        return False

    # Otherwise: check if the maximum weight is below threshold
    max_weight = 0.0
    for group_element in vertex.groups:
        if group_element.weight > max_weight:
            max_weight = group_element.weight

    return max_weight < weight_threshold


def build_kdtree_for_valid_vertices(obj, weight_threshold, only_without_groups, candidate_indices):
    """
    Builds a KD-Tree containing all vertices that are considered
    "valid" (NOT unweighted) among candidate_indices.

    Returns:
        kd: KDTree instance (or None)
        valid_indices: list mapping KD index -> vertex index
        weights_by_vert: dict[vert_index] -> list[(group_index, weight)]
    """
    mesh = obj.data

    valid_vert_indices = []
    weights_by_vert = {}

    for v_index in candidate_indices:
        if not is_unweighted_vertex(obj, v_index, weight_threshold, only_without_groups):
            valid_vert_indices.append(v_index)
            weights_by_vert[v_index] = get_vertex_weights(obj, v_index)

    if not valid_vert_indices:
        return None, [], {}

    kd = kdtree.KDTree(len(valid_vert_indices))
    for kd_index, v_index in enumerate(valid_vert_indices):
        kd.insert(mesh.vertices[v_index].co, kd_index)
    kd.balance()

    return kd, valid_vert_indices, weights_by_vert


def copy_weights_from_vertex(obj,
                             source_vert_index,
                             target_vert_index,
                             weights_by_vert,
                             clear_existing_groups=True):
    """
    Copies all vertex-group weights from source_vert_index to
    target_vert_index. Optionally clears existing groups on
    the target before copying.
    """
    mesh = obj.data
    vertex_groups = obj.vertex_groups

    source_weights = weights_by_vert.get(source_vert_index, [])
    target_vertex = mesh.vertices[target_vert_index]

    # Clear existing groups if requested
    if clear_existing_groups and target_vertex.groups:
        for group_element in list(target_vertex.groups):
            group = vertex_groups[group_element.group]
            group.remove([target_vert_index])

    # Apply all source weights to the target
    for group_index, weight in source_weights:
        vertex_groups[group_index].add([target_vert_index], weight, 'REPLACE')


def get_candidate_vertex_indices(obj, use_selected_only):
    """
    Returns a list of vertex indices we want to consider:
      - all vertices, or
      - only selected ones (if use_selected_only is True).
    """
    mesh = obj.data
    if not use_selected_only:
        return list(range(len(mesh.vertices)))

    # Use selection from the mesh (valid in Object or Edit mode
    # after we switch to OBJECT).
    return [v.index for v in mesh.vertices if v.select]


def find_best_source_vertex(obj,
                            bad_vert_index,
                            kd,
                            valid_vert_indices,
                            weights_by_vert,
                            search_radius):
    """
    For the given bad_vert_index, find a suitable source vertex:

      - If search_radius <= 0.0:
            just return the globally nearest valid vertex.

      - Else:
            look for all valid vertices within search_radius and
            pick the one with the highest max weight. If multiple
            have the same max weight, pick the closest one.

    Returns:
        (source_vert_index, distance) or (None, None) if no candidate
        is found within the radius (when radius > 0).
    """
    mesh = obj.data
    v_co = mesh.vertices[bad_vert_index].co

    # No radius limit -> simple nearest
    if search_radius is None or search_radius <= 0.0:
        nearest_co, nearest_kd_index, dist = kd.find(v_co)
        source_vert_index = valid_vert_indices[nearest_kd_index]
        return source_vert_index, dist

    # Radius-limited search
    candidates = kd.find_range(v_co, search_radius)

    if not candidates:
        # No candidate within the radius
        return None, None

    best_source_vert_index = None
    best_score = -1.0
    best_dist = None

    for cand_co, cand_kd_index, dist in candidates:
        source_vert_index = valid_vert_indices[cand_kd_index]
        weights_list = weights_by_vert.get(source_vert_index, [])

        if not weights_list:
            continue

        # Score: highest single weight among all groups
        # (ties are broken by distance).
        max_w = 0.0
        for _group_idx, w in weights_list:
            if w > max_w:
                max_w = w

        if max_w > best_score or (max_w == best_score and (best_dist is None or dist < best_dist)):
            best_score = max_w
            best_dist = dist
            best_source_vert_index = source_vert_index

    if best_source_vert_index is None:
        return None, None

    return best_source_vert_index, best_dist


# ============================================================
# Main Operation
# ============================================================

def main():
    obj = bpy.context.active_object

    if obj is None or obj.type != 'MESH':
        print("Error: Active object is not a mesh.")
        return

    if not obj.vertex_groups:
        print("Error: Mesh has no vertex groups; nothing to do.")
        return

    # Ensure we're in Object Mode for safe data access
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    mesh = obj.data

    candidate_indices = get_candidate_vertex_indices(obj, USE_SELECTED_VERTICES_ONLY)
    num_vertices = len(candidate_indices)

    print("=== Auto weight fill: start ===")
    print(f"Object:                 {obj.name}")
    print(f"Total mesh vertices:    {len(mesh.vertices)}")
    print(f"Vertices considered:    {num_vertices}")
    print(f"WEIGHT_THRESHOLD:       {WEIGHT_THRESHOLD}")
    print(f"CLEAR_EXISTING_GROUPS:  {CLEAR_EXISTING_GROUPS}")
    print(f"ONLY_WITHOUT_GROUPS:    {ONLY_VERTICES_WITHOUT_GROUPS}")
    print(f"USE_SELECTED_ONLY:      {USE_SELECTED_VERTICES_ONLY}")
    print(f"SEARCH_RADIUS:          {SEARCH_RADIUS}")
    print(f"N_DEBUG_PRINTS:         {N_DEBUG_PRINTS}")

    # Build KD-Tree of valid vertices (within the candidate set)
    kd, valid_vert_indices, weights_by_vert = build_kdtree_for_valid_vertices(
        obj=obj,
        weight_threshold=WEIGHT_THRESHOLD,
        only_without_groups=ONLY_VERTICES_WITHOUT_GROUPS,
        candidate_indices=candidate_indices
    )

    if kd is None or not valid_vert_indices:
        print("No vertices with sufficient weight found; nothing to copy from.")
        return

    num_fixed = 0
    num_unweighted_initial = 0
    num_no_source_found = 0

    # First pass: fix all "bad" vertices
    for v_index in candidate_indices:
        if is_unweighted_vertex(obj, v_index, WEIGHT_THRESHOLD, ONLY_VERTICES_WITHOUT_GROUPS):
            num_unweighted_initial += 1

            source_vert_index, dist = find_best_source_vertex(
                obj=obj,
                bad_vert_index=v_index,
                kd=kd,
                valid_vert_indices=valid_vert_indices,
                weights_by_vert=weights_by_vert,
                search_radius=SEARCH_RADIUS
            )

            if source_vert_index is None:
                # No candidate within radius (when radius > 0)
                num_no_source_found += 1
                continue

            copy_weights_from_vertex(
                obj=obj,
                source_vert_index=source_vert_index,
                target_vert_index=v_index,
                weights_by_vert=weights_by_vert,
                clear_existing_groups=CLEAR_EXISTING_GROUPS
            )
            num_fixed += 1

            # Optional debug: print every N_DEBUG_PRINTS fixed vertices
            if N_DEBUG_PRINTS > 0 and (num_fixed % N_DEBUG_PRINTS == 0):
                print(
                    f"[Debug] Fixed vertex {v_index} using source vertex "
                    f"{source_vert_index}, distance={dist:.6f} "
                    f"(fixed so far: {num_fixed})"
                )

    # Second pass: check how many are still effectively unweighted
    remaining_bad = [
        v_index for v_index in candidate_indices
        if is_unweighted_vertex(obj, v_index, WEIGHT_THRESHOLD, ONLY_VERTICES_WITHOUT_GROUPS)
    ]

    print("=== Auto weight fill: finished ===")
    print(f"Vertices initially unweighted (or below threshold): {num_unweighted_initial}")
    print(f"Vertices fixed:                                      {num_fixed}")
    print(f"Vertices still unweighted after pass:               {len(remaining_bad)}")
    if SEARCH_RADIUS > 0.0:
        print(f"  of which had no source inside radius:             {num_no_source_found}")

    if remaining_bad:
        print("Hint: If this number is unexpectedly high,")
        print("  - try lowering WEIGHT_THRESHOLD, and/or")
        print("  - increase SEARCH_RADIUS so that more source")
        print("    vertices are considered.")

    # --- Small popup summary in the Blender UI ---
    def _draw_popup(self, context):
        layout = self.layout
        layout.label(text=f"Initially unweighted: {num_unweighted_initial}")
        layout.label(text=f"Fixed: {num_fixed}")
        layout.label(text=f"Still unweighted: {len(remaining_bad)}")
        if SEARCH_RADIUS > 0.0:
            layout.label(text=f"No source in radius: {num_no_source_found}")

    bpy.context.window_manager.popup_menu(
        _draw_popup, title="Auto Weight Fill", icon='INFO'
    )


# Run immediately when executed from Blender's Text Editor
if __name__ == "__main__":
    main()
