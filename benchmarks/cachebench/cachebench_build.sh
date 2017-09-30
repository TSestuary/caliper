build_cachebench() {
    CURDIR=$(cd `dirname $0`; pwd)
    pushd ${CURDIR}/benchmarks/cachebench/ansible > /dev/null
    ansible-playbook -i hosts site.yml
    popd > /dev/null
}

build_cachebench

