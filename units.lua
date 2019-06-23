
require "tundra.syntax.glob"
require "tundra.syntax.files"
local native = require "tundra.native"

ExternalLibrary {
    Name = "defaultConfiguration",
    Pass = "CompileGenerator",
    Propagate = {
        Libs = {Config="win32-*-*"; "User32.lib", "Gdi32.lib", "Ws2_32.lib", "shell32.lib", "winmm.lib"},
    },
}  

Program {
  Name = "lepton",
  Sources = {
    "lepton/dependencies/md5/md5.c",
    "lepton/dependencies/zlib/inflate.c",
    "lepton/dependencies/zlib/inflate.h",
    "lepton/dependencies/zlib/gzguts.h",
    "lepton/dependencies/zlib/infback.c",
    "lepton/dependencies/zlib/trees.c",
    "lepton/dependencies/zlib/adler32.c",
    "lepton/dependencies/zlib/gzread.c",
    "lepton/dependencies/zlib/gzwrite.c",
    "lepton/dependencies/zlib/gzlib.c",

    "lepton/dependencies/zlib/gzclose.c",
    "lepton/dependencies/zlib/inftrees.h",
    "lepton/dependencies/zlib/zconf.h",
    "lepton/dependencies/zlib/compress.c",
    "lepton/dependencies/zlib/crc32.c",
    "lepton/dependencies/zlib/crc32.h",
    "lepton/dependencies/zlib/trees.h",
    "lepton/dependencies/zlib/inftrees.c",
    "lepton/dependencies/zlib/zutil.c",
    "lepton/dependencies/zlib/zutil.h",
    "lepton/dependencies/zlib/zlib.h",
    "lepton/dependencies/zlib/inffixed.h",
    "lepton/dependencies/zlib/deflate.c",
    "lepton/dependencies/zlib/inffast.h",
    "lepton/dependencies/zlib/inffast.c",
    "lepton/dependencies/zlib/uncompr.c",
    "lepton/dependencies/zlib/deflate.h",
    "lepton/dependencies/brotli/c/include/brotli/encode.h",
    "lepton/dependencies/brotli/c/include/brotli/types.h",
    "lepton/dependencies/brotli/c/include/brotli/decode.h",
    "lepton/dependencies/brotli/c/include/brotli/port.h",
    "lepton/dependencies/brotli/c/common/constants.h",
    "lepton/dependencies/brotli/c/common/version.h",
    "lepton/dependencies/brotli/c/common/dictionary.h",
    "lepton/dependencies/brotli/c/common/dictionary.c",
    "lepton/dependencies/brotli/c/enc/block_encoder_inc.h",
    "lepton/dependencies/brotli/c/enc/memory.c",
    "lepton/dependencies/brotli/c/enc/bit_cost.h",
    "lepton/dependencies/brotli/c/enc/ringbuffer.h",
    "lepton/dependencies/brotli/c/enc/entropy_encode.c",
    "lepton/dependencies/brotli/c/enc/quality.h",
    "lepton/dependencies/brotli/c/enc/utf8_util.h",
    "lepton/dependencies/brotli/c/enc/block_splitter_inc.h",
    "lepton/dependencies/brotli/c/enc/block_splitter.h",
    "lepton/dependencies/brotli/c/enc/compress_fragment.c",
    "lepton/dependencies/brotli/c/enc/utf8_util.c",
    "lepton/dependencies/brotli/c/enc/cluster_inc.h",
    "lepton/dependencies/brotli/c/enc/cluster.h",
    "lepton/dependencies/brotli/c/enc/literal_cost.c",
    "lepton/dependencies/brotli/c/enc/static_dict.c",
    "lepton/dependencies/brotli/c/enc/backward_references_hq.c",
    "lepton/dependencies/brotli/c/enc/hash.h",
    "lepton/dependencies/brotli/c/enc/literal_cost.h",
    "lepton/dependencies/brotli/c/enc/compress_fragment_two_pass.c",
    "lepton/dependencies/brotli/c/enc/dictionary_hash.c",
    "lepton/dependencies/brotli/c/enc/entropy_encode.h",
    "lepton/dependencies/brotli/c/enc/command.h",
    "lepton/dependencies/brotli/c/enc/metablock_inc.h",
    "lepton/dependencies/brotli/c/enc/context.h",
    "lepton/dependencies/brotli/c/enc/metablock.h",
    "lepton/dependencies/brotli/c/enc/hash_longest_match_quickly_inc.h",
    "lepton/dependencies/brotli/c/enc/hash_longest_match_inc.h",
    "lepton/dependencies/brotli/c/enc/hash_to_binary_tree_inc.h",
    "lepton/dependencies/brotli/c/enc/backward_references.h",
    "lepton/dependencies/brotli/c/enc/find_match_length.h",
    "lepton/dependencies/brotli/c/enc/prefix.h",
    "lepton/dependencies/brotli/c/enc/static_dict.h",
    "lepton/dependencies/brotli/c/enc/cluster.c",
    "lepton/dependencies/brotli/c/enc/brotli_bit_stream.h",
    "lepton/dependencies/brotli/c/enc/bit_cost_inc.h",
    "lepton/dependencies/brotli/c/enc/metablock.c",
    "lepton/dependencies/brotli/c/enc/backward_references_hq.h",
    "lepton/dependencies/brotli/c/enc/write_bits.h",
    "lepton/dependencies/brotli/c/enc/entropy_encode_static.h",
    "lepton/dependencies/brotli/c/enc/histogram.c",
    "lepton/dependencies/brotli/c/enc/encode.c",
    "lepton/dependencies/brotli/c/enc/port.h",
    "lepton/dependencies/brotli/c/enc/compress_fragment.h",
    "lepton/dependencies/brotli/c/enc/static_dict_lut.h",
    "lepton/dependencies/brotli/c/enc/histogram.h",
    "lepton/dependencies/brotli/c/enc/hash_forgetful_chain_inc.h",
    "lepton/dependencies/brotli/c/enc/block_splitter.c",
    "lepton/dependencies/brotli/c/enc/brotli_bit_stream.c",
    "lepton/dependencies/brotli/c/enc/compress_fragment_two_pass.h",
    "lepton/dependencies/brotli/c/enc/backward_references_inc.h",
    "lepton/dependencies/brotli/c/enc/bit_cost.c",
    "lepton/dependencies/brotli/c/enc/backward_references.c",
    "lepton/dependencies/brotli/c/enc/histogram_inc.h",
    "lepton/dependencies/brotli/c/enc/hash_longest_match64_inc.h",
    "lepton/dependencies/brotli/c/enc/fast_log.h",
    "lepton/dependencies/brotli/c/enc/memory.h",
    "lepton/dependencies/brotli/c/enc/dictionary_hash.h",
    "lepton/dependencies/brotli/c/dec/state.h",
    "lepton/dependencies/brotli/c/dec/huffman.h",
    "lepton/dependencies/brotli/c/dec/transform.h",
    "lepton/dependencies/brotli/c/dec/state.c",
    "lepton/dependencies/brotli/c/dec/bit_reader.c",
    "lepton/dependencies/brotli/c/dec/huffman.c",
    "lepton/dependencies/brotli/c/dec/context.h",
    "lepton/dependencies/brotli/c/dec/bit_reader.h",
    "lepton/dependencies/brotli/c/dec/prefix.h",
    "lepton/dependencies/brotli/c/dec/port.h",
    "lepton/dependencies/brotli/c/dec/decode.c",
    "lepton/src/lepton/base_coders.hh",
    "lepton/src/lepton/simple_encoder.hh",
    "lepton/src/lepton/bitops.cc",
    "lepton/src/lepton/bitops.hh",
    "lepton/src/lepton/component_info.hh",
    "lepton/src/lepton/htables.hh",
    "lepton/src/lepton/fork_serve.cc",
    "lepton/src/lepton/fork_serve.hh",
    "lepton/src/lepton/thread_handoff.cc",
    "lepton/src/lepton/thread_handoff.hh",
    "lepton/src/lepton/socket_serve.cc",
    "lepton/src/lepton/socket_serve.hh",
    "lepton/src/lepton/jpgcoder.cc",
    "lepton/src/lepton/concat.cc",
    "lepton/src/lepton/smalljpg.hh",
    "lepton/src/lepton/benchmark.cc",
    "lepton/src/lepton/main.cc",
    "lepton/src/lepton/validation.cc",
    "lepton/src/lepton/validation.hh",
    "lepton/src/lepton/generic_compress.cc",
    "lepton/src/lepton/generic_compress.hh",
    "lepton/src/lepton/recoder.cc",
    "lepton/src/lepton/recoder.hh",
    "lepton/src/lepton/idct.cc",
    "lepton/src/lepton/idct.hh",
    "lepton/src/lepton/uncompressed_components.cc",
    "lepton/src/lepton/jpgcoder.hh",
    "lepton/src/lepton/uncompressed_components.hh",
    "lepton/src/lepton/lepton_codec.cc",
    "lepton/src/lepton/lepton_codec.hh",
    "lepton/src/lepton/vp8_decoder.cc",
    "lepton/src/lepton/simple_decoder.cc",
    "lepton/src/lepton/vp8_decoder.hh",
    "lepton/src/lepton/simple_decoder.hh",
    "lepton/src/lepton/vp8_encoder.cc",
    "lepton/src/lepton/simple_encoder.cc",
    "lepton/src/lepton/vp8_encoder.hh",
    "lepton/src/io/Allocator.hh",
    "lepton/src/io/BufferedIO.hh",
    "lepton/src/io/ZlibCompression.cc",
    "lepton/src/io/ZlibCompression.hh",
    "lepton/src/io/BrotliCompression.cc",
    "lepton/src/io/BrotliCompression.hh",
    "lepton/src/io/Seccomp.hh",
    "lepton/src/io/Seccomp.cc",
    "lepton/src/io/seccomp-bpf.hh",
    "lepton/src/io/MemReadWriter.cc",
    "lepton/src/io/Error.hh",
    "lepton/src/io/Reader.hh",
    "lepton/src/io/MuxReader.hh",
    "lepton/src/io/ioutil.hh",
    "lepton/src/io/ioutil.cc",
    "lepton/src/io/Zlib0.hh",
    "lepton/src/io/Zlib0.cc",
    "lepton/src/io/DecoderPlatform.hh",
    "lepton/src/vp8/util/generic_worker.hh",
    "lepton/src/vp8/util/options.hh",
    "lepton/src/vp8/util/generic_worker.cc",
    "lepton/src/vp8/util/memory.cc",
    "lepton/src/vp8/util/memory.hh",
    "lepton/src/vp8/util/billing.cc",
    "lepton/src/vp8/util/billing.hh",
    "lepton/src/vp8/util/debug.cc",
    "lepton/src/vp8/util/debug.hh",
    "lepton/src/vp8/util/nd_array.hh",
    "lepton/src/vp8/util/aligned_block.hh",
    "lepton/src/vp8/util/block_based_image.hh",
    "lepton/src/vp8/model/JpegArithmeticCoder.cc",
    "lepton/src/vp8/model/JpegArithmeticCoder.hh",
    "lepton/src/vp8/model/branch.hh",
    "lepton/src/vp8/model/model.cc",
    "lepton/src/vp8/model/model.hh",
    "lepton/src/vp8/model/numeric.cc",
    "lepton/src/vp8/model/numeric.hh",
    "lepton/src/vp8/model/jpeg_meta.hh",
    "lepton/src/vp8/encoder/encoder.cc",
    "lepton/src/vp8/decoder/decoder.cc",
    "lepton/src/vp8/encoder/bool_encoder.hh",
    "lepton/src/vp8/decoder/bool_decoder.hh",
    "lepton/src/vp8/encoder/boolwriter.hh",
    "lepton/src/vp8/encoder/boolwriter.cc",
    "lepton/src/vp8/decoder/boolreader.hh",
    "lepton/src/vp8/decoder/boolreader.cc",
    "lepton/src/vp8/encoder/vpx_bool_writer.hh",
    "lepton/src/vp8/decoder/vpx_bool_reader.hh",
    "lepton/src/io/MemMgrAllocator.cc",
    "lepton/src/io/MemMgrAllocator.hh",
  },
  Env = {
    CPPDEFS = {
      --"ENABLE_ANS_EXPERIMENTAL", ?
      "DEFAULT_SINGLE_THREAD",
      "DEFAULT_ALLOW_PROGRESSIVE",
      "HIGH_MEMORY",
      --"SKIP_VALIDATION", ?
      "NDEBUG",
    },
    CCOPTS = {
      {Config="*-clang-*"; "-std=c99", "-O3"},
    },
    CXXOPTS = {
      {Config="*-clang-*"; "-mssse3", "-msse4.2", "-march=core-avx2", "-std=c++11",  "-fno-exceptions",  "-fno-rtti", "-O3"},
      {Config="*-msvc-*"; "-D_HAS_EXCEPTIONS=0", "-GR-", "/arch:SSE2", "/arch:AVX2", "-D__SSE2__"},
    },

    CPPPATH = {
      "lepton/src/vp8/util",
      "lepton/dependencies/brotli/c/include",
      "lepton/src/vp8/model",
      "lepton/src/vp8/encoder",
      "lepton/src/vp8/decoder",
    },
  },
  Libs = {Config="win32-*-*"; "Comdlg32.lib", "Ole32.lib" },
  Depends = {
       "defaultConfiguration"
  },
}
Default "lepton"

--============================================================================================--  

Program {
  Name = "meowhash",
  Sources = {
    "meow_hash/meow_example.cpp",
  },
  Env = {
    CPPDEFS = {
    },
    CXXOPTS = {
      {Config="*-clang-*"; "-O3", "-mavx", "-maes"},
      {Config="*-msvc-*"; "-nologo", "-FC", "-Oi", "-O2", "-Zi"},
    },

    CPPPATH = {
      "meow_hash",
    },
  },
  Libs = {Config="win32-*-*"; "Comdlg32.lib", "Ole32.lib" },
  Depends = {
       "defaultConfiguration"
  },
}
Default "meowhash"

Program {
  Name = "meowhash_test",
  Sources = {
    "meow_hash/util/meow_test.cpp",
  },
  Env = {
    CPPDEFS = {
    },
    CXXOPTS = {
      {Config="*-clang-*"; "-O3", "-mavx", "-maes"},
      {Config="*-msvc-*"; "-nologo", "-FC", "-Oi", "-O2", "-Zi"},
    },

    CPPPATH = {
      "meow_hash",
    },
  },
  Libs = {Config="win32-*-*"; "Comdlg32.lib", "Ole32.lib" },
  Depends = {
       "defaultConfiguration"
  },
}

--============================================================================================--  

Program {
  Name = "zpaq715",
  Sources = {
    "zpaq715/zpaq.cpp",
    "zpaq715/libzpaq.cpp",
  },
  Env = {
    CPPDEFS = {
      {Config="*-clang-*"; "unix"},
    },
    CXXOPTS = {
      {Config="*-clang-*"; "-O3", "-mavx", "-maes"},
      {Config="*-msvc-*"; "-nologo", "-FC", "-Oi", "-O2", "-Zi"},
    },
    CPPPATH = {
      "zpaq715",
    },
  },
  Libs = {Config="win32-*-*"; "Comdlg32.lib", "Ole32.lib", "Advapi32.lib"},
  Depends = {
       "defaultConfiguration"
  },
}
Default "zpaq715"

--============================================================================================--  

Program {
  Name = "precomp-cpp",
  Sources = {
    "precomp-cpp/precomp.cpp",
    FGlob {
       Dir = "precomp-cpp/contrib",
       Extensions = { ".c", ".cpp" },
       Filters = {
         {Config="DISABLED"; Pattern = "crc32_tablegen.c"},
         {Config="DISABLED"; Pattern = "crc64_tablegen.c"},
         {Config="DISABLED"; Pattern = "main.cpp"},
         {Config="DISABLED"; Pattern = "main2.cpp"},
         {Config="DISABLED"; Pattern = "fastpos_tablegen.c"},
         {Config="DISABLED"; Pattern = "price_tablegen.c"},
       },
    },
  },
  Env = {
    CPPDEFS = {
      "BUILD_LIB", "BIT64",
      {Config="*-clang-*"; "LINUX", "UNIX", "HAVE_STDBOOL_H"},
      {Config="*-msvc-*"; "_UNICODE", "UNICODE"},
    },
    CXXOPTS = {
    },
    CPPPATH = {
      "precomp-cpp/contrib/liblzma/api",
      "precomp-cpp/contrib/liblzma/common",
      "precomp-cpp/contrib/liblzma/check",
      "precomp-cpp/contrib/liblzma/lzma",
      "precomp-cpp/contrib/liblzma/lz",
      "precomp-cpp/contrib/liblzma/rangecoder",
      "precomp-cpp/contrib/liblzma/simple",
      "precomp-cpp/contrib/liblzma/delta",
    },
  },
  Libs = {Config="win32-*-*"; "Comdlg32.lib", "Ole32.lib" },
  Depends = {
       "defaultConfiguration"
  },
}
Default "precomp-cpp"
