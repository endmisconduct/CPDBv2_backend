#!/usr/bin/env bash

args=(
    -i ansible/inventory/staging
    --tags "${1:-deploy}"
    --vault-password-file ../vault_pass.txt
)
if [[ $2 ]]; then
    args+=(--extra-vars "${2}")
fi

ansible-playbook ansible/staging.yml "${args[@]}"
