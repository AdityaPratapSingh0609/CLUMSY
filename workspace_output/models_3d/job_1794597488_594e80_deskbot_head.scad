// J.A.R.V.I.S. Parametric CAD Model (.scad) — Deskbot
// Shape Archetype: deskbot_head
$fn = 64;

module jarvis_model() {
    difference() {
        minkowski() {
            cube([24, 17, 16], center=true);
            sphere(r=2.5);
        }
        translate([0, 8.5, 0]) cube([19, 4, 9], center=true);
    }
    translate([-5, 7.5, 0]) sphere(r=2.8);
    translate([ 5, 7.5, 0]) sphere(r=2.8);
}

jarvis_model();
