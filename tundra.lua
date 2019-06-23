
local common = {
	Env = {
    
		CXXOPTS = {
      {Config="*-clang-*"; "-std=c++14", "-stdlib=libstdc++", "-fPIC", "-fcolor-diagnostics"},
      {Config="*-clang-debug"; "-g", "-gsplit-dwarf", "-O0", "-fno-omit-frame-pointer"},
      {Config="*-clang-release"; "-Os", "-fdata-sections", "-ffunction-sections", "-fno-asynchronous-unwind-tables"},
      -- "-flto=thin"
      --{Config="*-clang-release"; "-fsave-optimization-record"},
      {Config="*-msvc-*"; "/FS", "/diagnostics:caret", "/cgthreads8" },      -- "-showIncludes"
      -- O1 is minsize, O2 is maxspeed
      -- Oi generates intrinsic functions
      -- Ox uses maximum optimization
      -- Oy omits frame pointer (x86 only)
      -- fp:fast generates fast float handling
      -- Gy enable function level linking
      -- Gw optimize global data
      -- Gr fastcall convention
      -- GS Buffer Security Checks
      -- GR run-time type information
      -- GL whole program optimization
      -- c generate object files only
      -- GF eliminate duplicate strings
      -- GT enable fibersafe optimizations
      -- MD multithreaded DLL (without debug)
      -- Zf faster PDB generation
      {Config="*-msvc-release"; "/Zi", "/DEBUG:full", "/O1", "/Oi", "/Oy", "/Qpar", "/fp:fast", "/Gy", "/Gw", "/Gr", "/GL", "/c", "/GS-", "/GR-", "/GF", "/GT", "/MD", "/Zf"},
    },
    CCOPTS = {
      {Config="*-msvc-*"; "/FS" },
      {Config="*-msvc-release"; "/Zi", "/DEBUG:full", "/O1", "/Oi", "/Oy", "/Qpar", "/fp:fast", "/Gy", "/Gw", "/Gr", "/GL", "/c", "/GS-", "/GR-", "/GF", "/GT", "/MD", "/Zf"},
    },
    PROGOPTS = {
      -- LTCG link time code generation
      {Config="*-msvc-release"; "/DEBUG:full", "/OPT:ref", "/PDB:t2-output/win32-msvc-release-default/animtest.pdb", "/LTCG",
                                },
                                --"/NODEFAULTLIB"
--      {Config="*-clang-*"; "-fuse-ld=lld"},           -- makes the executable a little bit bigger than the normal linker
      {Config="*-clang-release"; "-Wl,--gc-sections"},  -- "-flto=thin", "-Wl,--build-id"
    },
    LIBS = {
      {Config="*-clang-*"; "m", "Xrandr", "Xext", "X11", "dl", "stdc++", "pthread", "stdc++fs", "GL"},
    },
    LIBOPTS = {
      -- LTCG link time code generation
      {Config="*-msvc-release"; "/LTCG"},
      -- llvm-ar handles automatically link-time-optimization
    },
    CPPDEFS = {
      -- "SUPPORT_TRACELOG",
      {Config="*-*-debug"; "DEBUG=1", "SOKOL_TRACE_HOOKS",
                           "MICROPROFILE_ENABLED=0", "IMGUI_DISABLE_OBSOLETE_FUNCTIONS", "SOKOL_GLCORE33" },
      {Config="*-*-release"; "RELEASE=1", "NDEBUG=1", "DISABLE_CR", "MICROPROFILE_ENABLED=0", "SOKOL_GLCORE33"},
      {Config="win32-*-*"; "_WIN32", "NOMINMAX"},  -- "_X86_" "_WIN32_WINNT=0x0600",
    },
    GENERATE_PDB = {
      { Config = "*-msvc-release"; "0" },         -- setting this to 1 generates a much bigger executable!
      { Config = "*-msvc-debug"; "1" },
    },
	},
}

Build {
  IdeGenerationHints = {
    QtCreator = {
      SolutionName = "_AnimTest.pro",
    },
  },
	Passes = {
		CompileGenerator = { Name="Compile generator", BuildOrder = 1 },
		CodeGeneration = { Name="Generate sources", BuildOrder = 2 },
	},
	Units = {
      "units.lua",
   	},
	Configs = {
--    {
--       Name = "linux_x86-gcc",
--       DefaultOnHost = "linux",
--       Tools = { "gcc" },
--       Inherit = common,
--       SupportedHosts = { "linux" },
--       ReplaceEnv = {
--          -- Link with the C++ compiler to get the C++ standard library.
--          LD = "$(CXX)",
--       },
--    },
    {
       Name = "linux_x86-clang",
       DefaultOnHost = "linux",
       Tools = { "clang" },
       Inherit = common,
       SupportedHosts = { "linux" },
       ReplaceEnv = {
          CC = "clang-7",
          CXX = "clang++-7",
          LD = "clang-7",
          --LD = "ld.lld-7",
          LIB = "llvm-ar-7",
       },
    },
		{
			Name = "win32-msvc",
			DefaultOnHost = "windows",
			Tools = { { "msvc"; TargetArch="x86" } },
			Inherit = common,
		},
    {
      Name = "win64-msvc",
      SupportedHosts = { "windows" },
      Tools = { { "msvc"; TargetArch="x64" } },
      Inherit = common,
    },
	},
}
