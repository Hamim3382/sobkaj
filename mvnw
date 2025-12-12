#!/bin/sh
# ----------------------------------------------------------------------------
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Apache Maven Wrapper startup batch script, version 3.2.0
# ----------------------------------------------------------------------------

if [ -z "$JAVA_HOME" ] ; then
  JAVACMD="`which java`"
else
  JAVACMD="$JAVA_HOME/bin/java"
fi

if [ ! -x "$JAVACMD" ] ; then
  echo "The JAVA_HOME environment variable is not defined correctly, this environment" >&2
  echo "variable is needed to run this program." >&2
  exit 1
fi

MAVEN_PROJECTBASEDIR="${MAVEN_BASEDIR:-$(cd "$(dirname "$0")" && pwd)}"
MAVEN_OPTS="${MAVEN_OPTS:-}"

# Download maven wrapper jar if not present
WRAPPER_LAUNCHER="$MAVEN_PROJECTBASEDIR/.mvn/wrapper/maven-wrapper.jar"
WRAPPER_URL="https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar"

if [ ! -r "$WRAPPER_LAUNCHER" ]; then
  if [ -z "$MVNW_VERBOSE" ]; then
    echo "Downloading Maven wrapper..."
  fi
  mkdir -p "$MAVEN_PROJECTBASEDIR/.mvn/wrapper"
  
  if command -v wget > /dev/null 2>&1; then
    if [ "$MVNW_VERBOSE" = true ]; then
      echo "Using wget to download wrapper..."
    fi
    wget "$WRAPPER_URL" -O "$WRAPPER_LAUNCHER" || exit $?
  elif command -v curl > /dev/null 2>&1; then
    if [ "$MVNW_VERBOSE" = true ]; then
      echo "Using curl to download wrapper..."
    fi
    curl -o "$WRAPPER_LAUNCHER" "$WRAPPER_URL" -L || exit $?
  else
    echo "Cannot download maven-wrapper.jar: wget or curl not available." >&2
    exit 1
  fi
fi

# Execute maven with wrapper
exec "$JAVACMD" \
  $MAVEN_OPTS \
  -classpath "$WRAPPER_LAUNCHER" \
  org.apache.maven.wrapper.MavenWrapperMain "$@"
