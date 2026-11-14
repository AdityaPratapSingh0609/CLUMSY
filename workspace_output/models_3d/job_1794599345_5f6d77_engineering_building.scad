// J.A.R.V.I.S. Parametric Engineering CAD Model (.scad) — create an engineering 3d model of a building
// Archetype: engineering_building
$fn = 72;

module jarvis_engineering_assembly() {
    // Foundation & Structural Core
    translate([0, 0, -14]) cylinder(h=3, r=18, center=true);
    for (z = [-10 : 4 : 10]) {
        translate([0, 0, z]) cube([22, 18, 0.8], center=true);
    }
    for (x = [-9, 9]) for (y = [-7, 7]) {
        translate([x, y, 0]) cylinder(h=24, r=1.1, center=true);
    }
    translate([0, 0, 14]) sphere(r=4.5);
}

jarvis_engineering_assembly();
