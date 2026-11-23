#!/bin/sh
# Build the Rust course: page to publish (publish/rust-course.html) and the app (rust-course/index.html).
cd "$(dirname "$0")"
python3 build.py ../course.html rust-course.html content/*.yaml || exit 1
cp rust-course.html static_test.html
mkdir -p ../publish
python3 ../speed_pub.py rust-course.html ../publish/rust-course.html >/dev/null
python3 ../vendorize.py ../publish/rust-course.html ../rust-course/index.html
