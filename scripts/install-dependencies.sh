export DEBIAN_FRONTEND="noninteractive"
export GRADLE_HOME="/opt/gradle"
export JAVA_MAJOR_VERSION="8"
export GRADLE_VERSION="2.14.1"
export NODE_MAJOR_VERSION="10"

apt-get update
# Install Dependencies
apt-get install -y --no-install-recommends                                                          \
    gcc                                                                                             \
    g++                                                                                             \
    git                                                                                             \
    curl                                                                                            \
    unzip                                                                                           \
    gnupg                                                                                           \
    dirmngr                                                                                         \
    software-properties-common                                                                      \
    apt-utils                                                                                       \
    java-common                                                                                     \
    libicu-dev                                                                                      \
    `# Install Python and PIP`                                                                      \
    python3-dev                                                                                     \
    python3-pip                                                                                     \
    `# Install PostgreSQL`                                                                          \
    postgresql                                                                                      \
    postgresql-contrib
    
# Install Oracle Java
wget https://d3pxv6yz143wms.cloudfront.net/8.212.04.2/java-1.8.0-amazon-corretto-jdk_8.212.04-2_amd64.deb
dpkg --install java-1.8.0-amazon-corretto-jdk_8.212.04-2_amd64.deb

# echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
# add-apt-repository -y ppa:webupd8team/java
# apt-get update
# apt-get install -y --no-install-recommends oracle-java${JAVA_MAJOR_VERSION}-installer

# Install Gradle
mkdir ${GRADLE_HOME}
curl -sL https://services.gradle.org/distributions/gradle-${GRADLE_VERSION}-bin.zip -o gradle.zip
unzip -d ${GRADLE_HOME} gradle.zip
ln -s ${GRADLE_HOME}/gradle-${GRADLE_VERSION}/bin/gradle /usr/bin/gradle

# Install NodeJS
curl -sL https://deb.nodesource.com/setup_${NODE_MAJOR_VERSION}.x | bash -
apt-get install -y --no-install-recommends nodejs

# Install yarn
npm install -g yarn

# Create Python and PIP symbolic links
ln -s /usr/bin/python3 /usr/local/bin/python
ln -s /usr/bin/pip3    /usr/local/bin/pip
pip install --upgrade pip
pip install setuptools

# Uninstall unecessary packages
apt-get remove -y                                                                                   \
    curl                                                                                            \
    unzip                                                                                           \
    gnupg                                                                                           \
    dirmngr                                                                                         \
    software-properties-common

# Remove Cache
rm -rf /var/cache/oracle-jdk${JAVA_MAJOR_VERSION}-installer
rm -rf ./gradle.zip