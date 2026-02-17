#!/bin/sh

set -ex # включить расширенное отображение ошибок

cat russian_trusted_root_ca.cer | tee -a $(python -m certifi)

exit 0