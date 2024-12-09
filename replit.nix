{pkgs}: {
  deps = [
    pkgs.azure-cli
    pkgs.openssl
    pkgs.glibcLocales
    pkgs.postgresql
  ];
}
