{ pkgs }: {
    deps = [
        pkgs.python310
        pkgs.python310Packages.pip
        pkgs.python310Packages.setuptools
        pkgs.postgresql
        pkgs.redis
    ];
}