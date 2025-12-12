@REM ----------------------------------------------------------------------------
@REM Licensed to the Apache Software Foundation (ASF) under one
@REM or more contributor license agreements.  See the NOTICE file
@REM distributed with this work for additional information
@REM regarding copyright ownership.  The ASF licenses this file
@REM to you under the Apache License, Version 2.0 (the
@REM "License"); you may not use this file except in compliance
@REM with the License.  You may obtain a copy of the License at
@REM
@REM    https://www.apache.org/licenses/LICENSE-2.0
@REM
@REM Unless required by applicable law or agreed to in writing,
@REM software distributed under the License is distributed on an
@REM "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
@REM KIND, either express or implied.  See the License for the
@REM specific language governing permissions and limitations
@REM under the License.
@REM ----------------------------------------------------------------------------

@REM ----------------------------------------------------------------------------
@REM Apache Maven Wrapper startup batch script, version 3.2.0
@REM ----------------------------------------------------------------------------

@IF "%__MVNW_ARG0__%"=="" (SET __MVNW_ARG0__=%~dpnx0)
@SET __MVNW_CMD__=
@SET __MVNW_ERROR__=
@SET __MVNW_PSMODULEP__=%PSModulePath%
@SET PSModulePath=
@FOR /F "usebackq tokens=1* delims==" %%A IN (`powershell -noprofile "& {$scriptDir='%~dp0'; $env:__MVNW_ARG0__=''; $env:__MVNW_URL__='https://repo.maven.apache.org/maven2/org/apache/maven/wrapper/maven-wrapper/3.2.0/maven-wrapper-3.2.0.jar'; foreach ($f in @('%~dp0.mvn\wrapper\maven-wrapper.properties','%~dp0mvnw.properties')) { if (Test-Path $f) { foreach ($l in (Get-Content $f)) { if ($l -match '^(distributionUrl|wrapperUrl)\s*=\s*(.*)') { if ($matches[1] -eq 'wrapperUrl') { $env:__MVNW_URL__ = $matches[2] } } } } }; $env:__MVNW_CMD__='powershell -noprofile -executionpolicy bypass -file \"%~dp0mvnw.ps1\" '; $env:__MVNW_ERROR__=''; $null | cmd /c 'echo __MVNW_CMD__=!__MVNW_CMD__!'\r\n'echo __MVNW_ERROR__=!__MVNW_ERROR__!' }"`) DO @SET "%%A%%B"
@SET PSModulePath=%__MVNW_PSMODULEP__%
@IF "%__MVNW_ERROR__%"=="" IF "%__MVNW_CMD__%"=="" (@ECHO Error downloading Maven wrapper properties 1>&2 && @EXIT /B 1)
@IF NOT "%__MVNW_ERROR__%"=="" (@ECHO %__MVNW_ERROR__% 1>&2 && @EXIT /B 1)
%__MVNW_CMD__% %*
