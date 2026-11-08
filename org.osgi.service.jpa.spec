Name:		org.osgi.service.jpa
Version:	1.1.1
Release:	1
Summary:	OSGi JPA Service API
Group:		Development/Java
License:	ASL 2.0
URL:		https://docs.osgi.org/
Source0:	https://repo1.maven.org/maven2/org/osgi/org.osgi.service.jpa/%{version}/org.osgi.service.jpa-%{version}-sources.jar
Source1:	https://raw.githubusercontent.com/osgi/osgi/r8-cmpn-final/LICENSE#/org.osgi.service.jpa-%{version}-LICENSE

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildRequires:	mvn(jakarta.persistence:jakarta.persistence-api)
BuildRequires:	mvn(org.osgi:osgi.core)
BuildRequires:	mvn(org.osgi:osgi.annotation)
BuildRequires:	mvn(org.osgi:org.osgi.namespace.extender)
BuildSystem:	maven
BuildOption(install):	--file-name %{name}

%description
OSGi JPA Service 1.1.1. EntityManagerFactoryBuilder returns a
javax.persistence.EntityManagerFactory and the provider Bundle.
RequireJPAExtender inlines an osgi.extender requirement named osgi.jpa
at version 1.1. The service package version is 1.1.1. The extender
namespace and the versioning annotations are compile-time only. This
build targets Java 8.

%prep
%setup -q -c -T
# The builders' rpmuncompress passes a sources jar to tar.
python - %{SOURCE0} <<'PY'
import sys
import zipfile
zipfile.ZipFile(sys.argv[1]).extractall(".")
PY
rm -rf META-INF
cp -p %{SOURCE1} LICENSE
mkdir -p src/main/java
mv org src/main/java/
python - <<'PY'
from pathlib import Path
root = Path("src/main/java")
javas = sorted(path.relative_to(root).as_posix() for path in root.rglob("*.java"))
expected = [
    "org/osgi/service/jpa/EntityManagerFactoryBuilder.java",
    "org/osgi/service/jpa/annotations/RequireJPAExtender.java",
    "org/osgi/service/jpa/annotations/package-info.java",
    "org/osgi/service/jpa/package-info.java",
]
if javas != expected:
    raise SystemExit("java files changed")
if list(Path(".").rglob("module-info.java")) or list(Path(".").rglob("*.class")):
    raise SystemExit("unexpected input")
license_text = Path("LICENSE").read_text(encoding="utf-8")
if "Apache License" not in license_text or "Version 2.0" not in license_text:
    raise SystemExit("LICENSE is not Apache 2.0")
header = (root / "org/osgi/service/jpa/EntityManagerFactoryBuilder.java").read_text(encoding="utf-8")
if "SPDX-License-Identifier: Apache-2.0" not in header:
    raise SystemExit("source license header changed")

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.osgi</groupId>
  <artifactId>org.osgi.service.jpa</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>OSGi JPA Service</name>
  <description>OSGi JPA Service %{version}, packaged without a parent POM.</description>
  <url>https://docs.osgi.org/</url>
  <licenses>
    <license>
      <name>Apache-2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>8</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>jakarta.persistence</groupId>
      <artifactId>jakarta.persistence-api</artifactId>
      <version>2.2.3</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.core</artifactId>
      <version>6.0.0</version>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>osgi.annotation</artifactId>
      <version>8.1.0</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.osgi</groupId>
      <artifactId>org.osgi.namespace.extender</artifactId>
      <version>1.0.1</version>
      <scope>provided</scope>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <release>8</release>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <archive>
            <manifestEntries>
              <Automatic-Module-Name>org.osgi.service.jpa</Automatic-Module-Name>
              <Specification-Version>1.1</Specification-Version>
              <Implementation-Version>%{version}</Implementation-Version>
            </manifestEntries>
          </archive>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>org.osgi.service.jpa</artifactId>",
    "<artifactId>jakarta.persistence-api</artifactId>",
    "<version>%{version}</version>",
    "<release>8</release>",
    "</project.build.sourceEncoding>",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
if pom.count("<version>1.1.1</version>") != 1 or pom.count("<version>2.2.3</version>") != 1 or pom.count("<version>6.0.0</version>") != 1 or pom.count("<version>8.1.0</version>") != 1 or pom.count("<version>1.0.1</version>") != 1 or pom.count("<scope>provided</scope>") != 2:
    raise SystemExit("pom versions changed")
for needle in (
    "junit",
    "SNAPSHOT",
    "<source>",
    "<target>",
    "<parent>",
    "felix",
    "maven-bundle-plugin",
    "<artifactId>org.osgi.framework</artifactId>",
    "<artifactId>org.osgi.resource</artifactId>",
    "<artifactId>org.osgi.annotation.versioning</artifactId>",
    "<version>8.0.1</version>",
    "<version>1.1</version>",
    "projectbuild.sourceEncoding",
):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
PY

%build -a
java --module-path target/org.osgi.service.jpa-%{version}.jar --describe-module org.osgi.service.jpa > module-describe.txt
grep -q '^org\.osgi\.service\.jpa@' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }
python - <<'PY'
import zipfile
from pathlib import Path
jar = Path("target/org.osgi.service.jpa-%{version}.jar")
with zipfile.ZipFile(jar) as zf:
    classes = {name for name in zf.namelist() if name.endswith(".class")}
    required = {
        "org/osgi/service/jpa/EntityManagerFactoryBuilder.class",
        "org/osgi/service/jpa/annotations/RequireJPAExtender.class",
        "org/osgi/service/jpa/annotations/package-info.class",
        "org/osgi/service/jpa/package-info.class",
    }
    if classes != required:
        raise SystemExit("class set " + " ".join(sorted(classes)))
    builder = zf.read("org/osgi/service/jpa/EntityManagerFactoryBuilder.class")
    if b"javax/persistence/EntityManagerFactory" not in builder or b"org/osgi/framework/Bundle" not in builder:
        raise SystemExit("builder lost a type")
    if b"javax/persistence/spi/PersistenceProvider" in builder:
        raise SystemExit("builder kept a javadoc-only type")
    requirement = zf.read("org/osgi/service/jpa/annotations/RequireJPAExtender.class")
    if b"org/osgi/annotation/bundle/Requirement" not in requirement or b"osgi.extender" not in requirement or b"osgi.jpa" not in requirement or b"1.1" not in requirement:
        raise SystemExit("JPA extender requirement was not inlined")
    if b"ExtenderNamespace" in requirement or b"1.1.1" in requirement:
        raise SystemExit("JPA extender requirement kept a class reference")
    info = zf.read("org/osgi/service/jpa/package-info.class")
    if b"org/osgi/annotation/versioning/Version" not in info or b"1.1.1" not in info:
        raise SystemExit("service package version was not recorded")
    ann = zf.read("org/osgi/service/jpa/annotations/package-info.class")
    if b"org/osgi/annotation/versioning/Version" not in ann or b"1.1.1" in ann:
        raise SystemExit("annotation package version changed")
PY

%files -f .mfiles
%doc LICENSE
