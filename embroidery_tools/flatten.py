import svgpathtools
import pyclipper
import math
import itertools


def svg_path_to_pyclipper_path(svg_path):
    pc_path = []
    for line in svg_path:
        for point in line:
            pc_path.append(
                [point.real, point.imag]
            )  # Convert complex numbers to [x, y]
    return pc_path


def pyclipper_path_to_svg_path(pc_path):
    svg_path = svgpathtools.Path()
    for i in range(len(pc_path)):
        start_point = complex(pc_path[i][0], pc_path[i][1])
        end_point = complex(
            pc_path[(i + 1) % len(pc_path)][0], pc_path[(i + 1) % len(pc_path)][1]
        )
        svg_path.append(svgpathtools.Line(start_point, end_point))
    return svg_path


def ellipse_to_polygon(cx, cy, rx, ry, num_points=50):
    points = []
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        points.append([x, y])
    return points


def whitelist_attributes(attrs):
    return {
        key: value
        for key, value in attrs.items()
        if key in ("style", "id") or ":" in key
    }


def main():
    svg_file = "../input.svg"
    paths, all_attributes, svg_attributes = svgpathtools.svg2paths2(svg_file)

    pc_paths = []
    for path, attributes in zip(paths, all_attributes):
        if "cx" in attributes and "rx" in attributes:
            cx = float(attributes["cx"])
            cy = float(attributes["cy"])
            rx = float(attributes["rx"])
            ry = float(attributes["ry"])
            pc_paths.append(ellipse_to_polygon(cx, cy, rx, ry))
        else:
            pc_paths.append(svg_path_to_pyclipper_path(path))

    paths = {i: [p] for i, p in enumerate(reversed(pc_paths))}
    for p1, p2 in itertools.combinations(range(len(pc_paths)), 2):
        if not paths[p1] or not paths[p2]:
            continue
        pc = pyclipper.Pyclipper()
        pc.AddPaths(pyclipper.scale_to_clipper(paths[p1]), pyclipper.PT_CLIP, True)
        pc.AddPaths(pyclipper.scale_to_clipper(paths[p2]), pyclipper.PT_SUBJECT, True)
        if not pc.Execute(pyclipper.CT_INTERSECTION):
            continue
        paths[p2] = pyclipper.scale_from_clipper(
            pc.Execute(
                pyclipper.CT_DIFFERENCE, pyclipper.PFT_EVENODD, pyclipper.PFT_EVENODD
            )
        )

    result_paths = []
    new_attributes = []

    for path_list, attributes in zip(paths.values(), reversed(all_attributes)):
        for path in path_list:
            p = pyclipper_path_to_svg_path(path)
            result_paths.append(p)
            new_attributes.append(
                {
                    "d": pyclipper_path_to_svg_path(p).d(),
                    **whitelist_attributes(attributes),
                }
            )

    new_svg_file = "../output.svg"
    svgpathtools.wsvg(
        result_paths,
        attributes=new_attributes,
        svg_attributes=svg_attributes,
        filename=new_svg_file,
    )


if __name__ == "__main__":
    main()
