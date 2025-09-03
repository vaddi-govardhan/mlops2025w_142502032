#!/bin/bash

echo "Enter coefficients a, b and c: "
read a b c

d=$((b*b - 4*a*c))

echo "Discriminant = $d"

if [ $d -gt 0 ]
then
    echo "Roots are real and distinct"
    sqrt_d=$(echo "scale=4; sqrt($d)" | bc -l)
    root1=$(echo "scale=4; (-$b + $sqrt_d) / (2*$a)" | bc -l)
    root2=$(echo "scale=4; (-$b - $sqrt_d) / (2*$a)" | bc -l)
    echo "Root1 = $root1"
    echo "Root2 = $root2"

elif [ $d -eq 0 ]
then
    echo "Roots are real and equal"
    root=$(echo "scale=4; -$b / (2*$a)" | bc -l)
    echo "Root1 = Root2 = $root"

else
    echo "Roots are complex and imaginary"
    sqrt_d=$(echo "scale=4; sqrt(-$d)" | bc -l)
    real=$(echo "scale=4; -$b / (2*$a)" | bc -l)
    imag=$(echo "scale=4; $sqrt_d / (2*$a)" | bc -l)
    echo "Root1 = $real + i$imag"
    echo "Root2 = $real - i$imag"
fi

