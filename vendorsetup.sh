apply_patch() (
    local target_dir=$1
    local patch_path=$2
    local patch_file=${patch_path##*/}

    cd "$target_dir" || exit 1
    rm -f "$patch_file"
    wget -q "https://raw.githubusercontent.com/AOSP-for-vili/vili-patches/refs/heads/main/$patch_path" || {
        echo "Failed to download patch: $patch_path" >&2
        exit 1
    }

    local patch_subject
    patch_subject=$(git mailinfo /dev/null /dev/null < "$patch_file" | sed -n 's/^Subject: //p')

    if [ -n "$patch_subject" ] && git log -F --grep="$patch_subject" -n 1 --oneline | grep -q .; then
        echo "Patch already applied: $patch_path"
        rm -f "$patch_file"
        exit 0
    fi

    if git am "$patch_file"; then
        echo "Applied patch: $patch_path"
        rm -f "$patch_file"
    else
        echo "Failed to apply patch: $patch_path; aborting git am" >&2
        git am --abort
        rm -f "$patch_file"
        exit 1
    fi
)

cat vendor/xiaomi/camera/proprietary/system/priv-app/MiuiCamera/MiuiCamera.apk.part* > vendor/xiaomi/camera/proprietary/system/priv-app/MiuiCamera/MiuiCamera.apk

# Camera patches
echo 'Applying MIUI camera patches'
apply_patch "frameworks/base" "memecam/0001-camera-Add-backwards-compatible-CaptureResultExtras-.patch"
apply_patch "frameworks/base" "memecam/0002-core-camera2-StreamConfigurationMap-add-constructor-.patch"

# Device as Webcam camera related patch
echo 'Applying DeviceWebcamService patches'
apply_patch "packages/services/DeviceAsWebcam" "DeviceAsWebcam/0001-yuv-reswizzling.patch"
apply_patch "vendor/qcom/opensource/usb" "DeviceAsWebcam/0002-disable-1080p-advertising.patch"
