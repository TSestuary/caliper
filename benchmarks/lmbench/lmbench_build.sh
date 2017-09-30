build_lmbench() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/lmbench/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_lmbench
