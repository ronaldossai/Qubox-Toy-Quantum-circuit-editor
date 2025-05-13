OPENQASM 2.0;
include "qelib1.inc";

qreg q[3];
creg c[3];
x q[0];
x q[0];
y q[1];
h q[0];
x q[1];
h q[0];
y q[1];
cx q[0],q[1];
