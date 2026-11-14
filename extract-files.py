#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import glob
import os
from os import path

from extract_utils.file import File
from extract_utils.fixups_blob import (
    BlobFixupCtx,
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)
from extract_utils.makefiles import (
    MakefilesCtx,
    ProductPackagesCtx,
    write_mk_guard_begin,
    write_mk_guard_end,
)
from extract_utils.utils import (
    remove_dir_contents,
    run_cmd,
)

namespace_imports = [
    'vendor/xiaomi/camera',
]


def lib_fixup_system_variant(lib: str, partition: str, *args, **kwargs):
    return f'{lib}-system' if partition == 'system' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    'vendor.xiaomi.hardware.campostproc@1.0': lib_fixup_system_variant,
}


def split_apk(
    ctx: BlobFixupCtx,
    file: File,
    file_path: str,
    *args,
    **kwargs,
):
    for part in glob.glob(f'{file_path}.part*'):
        os.remove(part)
    run_cmd(['split', '--bytes=20M', '-d', file_path, f'{file_path}.part'])


blob_fixups: blob_fixups_user_type = {
    'system/lib64/libcamera_mianode_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so'),
    'system/lib64/libcamera_algoup_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so')
        .sig_replace('08 ad 40 f9', '08 a9 40 f9'),
    'system/lib64/libgui-xiaomi.so': blob_fixup()
        .replace_needed('android.hardware.graphics.common-V4-ndk.so', 'android.hardware.graphics.common-V7-ndk.so')
        .add_needed('libbinder_shim.so'),
    'system/priv-app/MiuiCamera/MiuiCamera.apk': blob_fixup()
        .call(split_apk),
}


def android_mk_guard_begin(ctx: MakefilesCtx, _: ProductPackagesCtx):
    write_mk_guard_begin('TARGET_DEVICE', 'vili', ctx.mk_out)
    ctx.mk_out.write(
        'CAMERA_LIBRARIES := libcamera_algoup_jni.xiaomi.so libcamera_mianode_jni.xiaomi.so\n\n'
        'CAMERA_SYMLINKS := $(addprefix $(TARGET_OUT_APPS_PRIVILEGED)/MiuiCamera/lib/arm64/,$(notdir $(CAMERA_LIBRARIES)))\n'
        '$(CAMERA_SYMLINKS): $(LOCAL_INSTALLED_MODULE)\n'
        '\t@echo "MiuiCamera lib link: $@"\n'
        '\t@mkdir -p $(dir $@)\n'
        '\t@rm -rf $@\n'
        '\t$(hide) ln -sf /system/lib64/$(notdir $@) $@\n\n'
        'ALL_DEFAULT_INSTALLED_MODULES += $(CAMERA_SYMLINKS)\n\n'
    )


def android_mk_guard_end(ctx: MakefilesCtx, _: ProductPackagesCtx):
    write_mk_guard_end(ctx.mk_out)


class CameraExtractUtilsModule(ExtractUtilsModule):
    def cleanup(self):
        remove_dir_contents(path.join(self.vendor_path, 'proprietary'))

        for proprietary_file in self.proprietary_files:
            vendor_path = self.proprietary_file_vendor_path(proprietary_file)
            os.makedirs(vendor_path, exist_ok=True)


module = CameraExtractUtilsModule(
    'camera',
    'xiaomi',
    device_rel_path='vendor/xiaomi/camera',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    skip_main_proprietary_file=True,
)

module.add_proprietary_file(
    'proprietary-files.txt',
    pre_makefile_generation_fn=android_mk_guard_begin,
    post_makefile_generation_fn=android_mk_guard_end,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
