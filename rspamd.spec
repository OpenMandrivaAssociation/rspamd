# Allow undefined symbols in plugins - they're resolved
# by dlopen
%define _disable_ld_no_undefined 1

%define rspamd_user rspamd
%define rspamd_group %{rspamd_user}
%define rspamd_home %{_localstatedir}/lib/rspamd
%define rspamd_logdir %{_localstatedir}/log/rspamd
%define rspamd_confdir %{_sysconfdir}/rspamd
%define rspamd_pluginsdir %{_datadir}/rspamd
%define rspamd_rulesdir %{_datadir}/rspamd/rules
%define rspamd_wwwdir %{_datadir}/rspamd/www

Summary:	Rapid spam filtering system
Name:		rspamd
Version:	3.10.0
Release:	2
Group:		System/Servers
License:	BSD-2-Clause
URL:		https://rspamd.com/
Source0:	https://github.com/vstakhov/rspamd/archive/%{version}.tar.gz
Source1:	%{name}.sysusers
Patch0:		rspamd-1.6.5-systemd-user.patch
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libevent)
BuildRequires:	pkgconfig(libcrypto)
BuildRequires:	pkgconfig(libssl)
BuildRequires:	pkgconfig(libpcre)
BuildRequires:	pkgconfig(luajit)
BuildRequires:	pkgconfig(fann)
BuildRequires:	pkgconfig(fmt)
BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(gdlib)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libsodium)
BuildRequires:	pkgconfig(libzstd)
BuildRequires:	pkgconfig(libunwind-llvm)
BuildRequires:	pkgconfig(libarchive) >= 3.0.0
BuildRequires:	cmake
BuildRequires:	magic-devel
BuildRequires:	perl
BuildRequires:	ragel
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	ninja
BuildRequires:	systemd-rpm-macros
Requires:	lua-lpeg
Requires(pre):	systemd
%systemd_requires

%description
Rspamd is a rapid, modular and lightweight spam filter. It is designed to work
with big amount of mail and can be easily extended with own filters written in
lua.

%prep
%autosetup -p1

%build
# ENABLE_LUAJIT is off because of lua 5.3 vs. luajit 5.1 mismatch
%cmake \
	-DCMAKE_C_OPT_FLAGS="%{optflags}" \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCONFDIR=%{_sysconfdir}/rspamd \
	-DMANDIR=%{_mandir} \
	-DDBDIR=%{_localstatedir}/lib/rspamd \
	-DRUNDIR=%{_localstatedir}/run/rspamd \
	-DWANT_SYSTEMD_UNITS=ON \
	-DSYSTEMDDIR=%{_unitdir} \
	-DSYSTEM_FMT:BOOL=ON \
	-DSYSTEM_ZSTD:BOOL=ON \
	-DENABLE_LUAJIT=ON \
	-DENABLE_HIREDIS=ON \
	-DLOGDIR=%{_localstatedir}/log/rspamd \
	-DEXAMPLESDIR=%{_datadir}/examples/rspamd \
	-DPLUGINSDIR=%{_datadir}/rspamd \
	-DLIBDIR=%{_libdir} \
	-DINCLUDEDIR=%{_includedir} \
	-DNO_SHARED=ON \
	-DDEBIAN_BUILD=1 \
	-DRSPAMD_GROUP=%{rspamd_group} \
	-DRSPAMD_USER=%{rspamd_user} \
	-G Ninja

%ninja_build

%install
%ninja_install -C build

install -d -p -m 0755 %{buildroot}%{rspamd_home}
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/local.d/
install -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/override.d/

sed -i -e 's,^User=.*,User=%{rspamd_user},g' %{buildroot}%{_unitdir}/%{name}.service

install -Dm 644 %{SOURCE1} %{buildroot}%{_sysusersdir}/rspamd.conf

mkdir -p %{buildroot}%{_tmpfilesdir}
cat >%{buildroot}%{_tmpfilesdir}/rspamd.conf <<'EOF'
d /run/rspamd 0755 rspamd rspamd -
d /var/lib/rspamd 0755 rspamd rspamd -
Z /var/lib/rspamd - rspamd rspamd -
d /var/log/rspamd 0755 rspamd rspamd -
Z /var/log/rspamd - rspamd rspamd -
EOF

%pre
%sysusers_create_package %{name}.conf %{SOURCE1}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%{_unitdir}/%{name}.service
%{_mandir}/man8/%{name}.*
%{_mandir}/man1/rspamc.*
%{_mandir}/man1/rspamadm.*
%{_bindir}/rspamd
%{_bindir}/rspamd_stats
%{_bindir}/rspamc
%{_bindir}/rspamadm
%config(noreplace) %{rspamd_confdir}/%{name}.conf
%config(noreplace) %{rspamd_confdir}/actions.conf
%config(noreplace) %{rspamd_confdir}/settings.conf
%config(noreplace) %{rspamd_confdir}/groups.conf
%config(noreplace) %{rspamd_confdir}/composites.conf
%config(noreplace) %{rspamd_confdir}/metrics.conf
%config(noreplace) %{rspamd_confdir}/modules.conf
%config(noreplace) %{rspamd_confdir}/statistic.conf
%config(noreplace) %{rspamd_confdir}/common.conf
%config(noreplace) %{rspamd_confdir}/modules.d/*
%config(noreplace) %{rspamd_confdir}/maps.d/*
%config(noreplace) %{_sysconfdir}/rspamd/cgp.inc
%config(noreplace) %{_sysconfdir}/rspamd/lang_detection.inc
%config(noreplace) %{_sysconfdir}/rspamd/logging.inc
%config(noreplace) %{_sysconfdir}/rspamd/options.inc
%config(noreplace) %{_sysconfdir}/rspamd/worker-controller.inc
%config(noreplace) %{_sysconfdir}/rspamd/worker-fuzzy.inc
%config(noreplace) %{_sysconfdir}/rspamd/worker-normal.inc
%config(noreplace) %{_sysconfdir}/rspamd/worker-proxy.inc
%dir %{rspamd_confdir}/scores.d
%{rspamd_confdir}/scores.d/*.conf
%{_sysusersdir}/rspamd.conf
%{_tmpfilesdir}/rspamd.conf
%attr(-,%{rspamd_user},%{rspamd_user}) %dir %{rspamd_home}
%dir %{rspamd_rulesdir}/controller
%dir %{rspamd_rulesdir}/regexp
%dir %{rspamd_rulesdir}
%dir %{rspamd_confdir}
%dir %{rspamd_confdir}/modules.d
%dir %{rspamd_confdir}/local.d
%dir %{rspamd_confdir}/override.d
%dir %{rspamd_pluginsdir}
%dir %{rspamd_wwwdir}
%{rspamd_rulesdir}/controller/*.lua
%{rspamd_rulesdir}/regexp/*.lua
%{rspamd_rulesdir}/*.lua
%{rspamd_wwwdir}/*
%{_libdir}/*.so
%{_datadir}/rspamd/effective_tld_names.dat
%{_datadir}/rspamd/elastic
%{_datadir}/rspamd/lualib
%{_datadir}/rspamd/languages
%{_datadir}/rspamd/*.lua
