set(CTEST_SITE "zeah.kitware.com")
set(CTEST_BUILD_NAME "Windows7_GPU_Master_Nightly")
set(CTEST_SOURCE_DIRECTORY "C:/workspace/VIAME-Seal-GPU")
set(CTEST_BINARY_DIRECTORY "C:/workspace/VIAME-Seal-GPU/build/")
set(CTEST_CMAKE_GENERATOR "Visual Studio 15 2017 Win64")
#set(CTEST_CMAKE_GENERATOR "Visual Studio 15 2017")
#set(CTEST_CMAKE_GENERATOR_PLATFORM "x64")
set(CTEST_BUILD_CONFIGURATION Release)
set(CTEST_PROJECT_NAME VIAME)
set(CTEST_BUILD_MODEL "Nightly")
set(CTEST_NIGHTLY_START_TIME "3:00:00 UTC")
set(CTEST_USE_LAUNCHERS 1)
include(CTestUseLaunchers)
set(OPTIONS 
  "-DCMAKE_BUILD_TYPE=Release"
  "-DCUDA_TOOLKIT_ROOT_DIR=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.1"
  "-DCUDNN_ROOT_DIR:PATH=C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.1/lib/x64"
  "-DVIAME_CREATE_PACKAGE=ON"
  "-DVIAME_ENABLE_CUDNN=ON"
  "-DVIAME_ENABLE_CUDA=ON"
  "-DVIAME_ENABLE_CAMTRAWL=OFF"
  "-DVIAME_ENABLE_PYTHON=ON"
  "-DVIAME_ENABLE_PYTHON-INTERNAL=ON"
  "-DVIAME_ENABLE_GDAL=OFF"
  "-DVIAME_ENABLE_SCALLOP_TK=OFF"
  "-DVIAME_ENABLE_PYTORCH=ON"
  "-DVIAME_PYTORCH_VERSION=1.7.1"
  "-DVIAME_ENABLE_PYTORCH-INTERNAL=OFF"
  "-DVIAME_ENABLE_PYTORCH-VIS-INTERNAL=OFF"
  "-DVIAME_ENABLE_PYTORCH-MMDET=ON"
  "-DVIAME_ENABLE_PYTORCH-NETHARN=ON"
  "-DVIAME_ENABLE_PYTORCH-PYSOT=OFF"
  "-DVIAME_ENABLE_ITK=ON"
  "-DVIAME_ENABLE_ITK_EXTRAS=ON"
  "-DVIAME_ENABLE_TENSORFLOW=ON"
  "-DVIAME_ENABLE_VIVIA=OFF"
  "-DVIAME_ENABLE_SEAL_TK=ON"
  "-DVIAME_DOWNLOAD_MODELS-ARCTIC-SEAL:BOOL=ON"
  "-DVIAME_FLETCH_BUILD_DIR=C:/tmp/fl3"
  "-DVIAME_KWIVER_BUILD_DIR=C:/tmp/kv3"
  "-DVIAME_PLUGINS_BUILD_DIR=C:/tmp/vm3"
)

set(platform Windows7)
