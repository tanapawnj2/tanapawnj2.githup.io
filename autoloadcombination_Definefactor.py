import win32com.client
from win32com.client import CastTo
import sys

def get_factor(name):
    while True:
        try:
            val = input(f"Factor {name}: ").strip()
            if val == "":
                print("กรุณากรอกตัวเลข")
                continue
            return float(val)
        except ValueError:
            print("กรุณากรอกตัวเลขเท่านั้น")

def get_combo_type():
    while True:
        val = input("Combination Type (0=ULS, 1=SLS): ").strip()
        if val in ["0", "1"]:
            return int(val)
        print("กรุณากรอก 0 หรือ 1 เท่านั้น")

def factor_str(factor):
    if factor == 1.0:
        return ""
    if factor == int(factor):
        return str(int(factor))
    return str(factor)

def cleanup_test_cases(cases):
    case_col = cases.GetAll()
    to_delete = []
    for i in range(1, case_col.Count + 1):
        rc = case_col.Get(i)
        if rc.Name.startswith("TEST"):
            to_delete.append(rc.Number)
    for num in to_delete:
        cases.Delete(num)

def create_combo(cases, combo_num, name, dl_nums, ll_nums, wl_num,
                 DL_FACTOR, LL_FACTOR, WL_FACTOR, COMBO_TYPE):
    cases.CreateCombination(combo_num, name, 0, 0, 0)
    combo = CastTo(cases.Get(combo_num), "IRobotCaseCombination")
    combo.CombinationType = COMBO_TYPE
    cf_server = combo.CaseFactors
    if DL_FACTOR != 0:
        for dl in dl_nums:
            cf_server.New(dl, float(DL_FACTOR))
    if LL_FACTOR != 0:
        for ll in ll_nums:
            cf_server.New(ll, float(LL_FACTOR))
    if WL_FACTOR != 0 and wl_num is not None:
        cf_server.New(wl_num, float(WL_FACTOR))
    type_str = "ULS" if COMBO_TYPE == 0 else "SLS"
    print(f"Created Combo {combo_num}: {name} [{type_str}]")

def auto_create_combinations():
    try:
        robot = win32com.client.Dispatch("Robot.Application")
    except:
        print("ERROR: Please open Robot Structural Analysis first")
        sys.exit()

    cases = robot.Project.Structure.Cases
    cleanup_test_cases(cases)
    case_col = cases.GetAll()

    dl_nums, ll_nums = [], []
    wl_nums, wl_names = [], []
    max_num = 0

    for i in range(1, case_col.Count + 1):
        rc = case_col.Get(i)
        if rc.Type == 1:
            if rc.Number > max_num:
                max_num = rc.Number
            continue
        n = rc.Nature
        if n == 0:
            dl_nums.append(rc.Number)
        elif n == 1:
            ll_nums.append(rc.Number)
        elif n == 2:
            wl_nums.append(rc.Number)
            wl_names.append(rc.Name)
        if rc.Number > max_num:
            max_num = rc.Number

    if not dl_nums:
        print("ERROR: No Dead Load Cases found")
        sys.exit()

    print(f"\nDetected Cases:")
    print(f"  Dead Load : {len(dl_nums)} Cases {dl_nums}")
    print(f"  Live Load : {len(ll_nums)} Cases {ll_nums}")
    print(f"  Wind Load : {len(wl_nums)} Cases {wl_names}")
    print("-" * 50)

    print("กรอก Load Factors (กรอก 0 = ไม่ใช้ Load นั้น):")
    DL_FACTOR = get_factor("Dead Load")

    if ll_nums:
        LL_FACTOR = get_factor("Live Load")
    else:
        LL_FACTOR = 0.0
        print("Live Load: ไม่พบ Cases -> LL_FACTOR = 0.0")

    if wl_nums:
        WL_FACTOR = get_factor("Wind Load")
    else:
        WL_FACTOR = 0.0
        print("Wind Load: ไม่พบ Cases -> WL_FACTOR = 0.0")

    COMBO_TYPE = get_combo_type()

    print("-" * 50)

    combo_num = max_num + 1
    print(f"Starting combo from Case: {combo_num}")
    print("-" * 50)
    created = 0

    if WL_FACTOR != 0 and wl_nums:
        for w in range(len(wl_nums)):
            name_parts = []
            if DL_FACTOR != 0: name_parts.append(f"{factor_str(DL_FACTOR)}DL")
            if LL_FACTOR != 0: name_parts.append(f"{factor_str(LL_FACTOR)}LL")
            name_parts.append(f"{factor_str(WL_FACTOR)}({wl_names[w]})")
            name = "+".join(name_parts)

            create_combo(cases, combo_num, name,
                        dl_nums, ll_nums, wl_nums[w],
                        DL_FACTOR, LL_FACTOR, WL_FACTOR, COMBO_TYPE)
            combo_num += 1
            created += 1
    else:
        name_parts = []
        if DL_FACTOR != 0: name_parts.append(f"{factor_str(DL_FACTOR)}DL")
        if LL_FACTOR != 0: name_parts.append(f"{factor_str(LL_FACTOR)}LL")
        name = "+".join(name_parts)

        create_combo(cases, combo_num, name,
                    dl_nums, ll_nums, None,
                    DL_FACTOR, LL_FACTOR, 0, COMBO_TYPE)
        combo_num += 1
        created += 1

    print("-" * 50)
    print(f"Done! Created {created} Combinations")
    input("\nกด Enter เพื่อปิด...")

if __name__ == "__main__":
    auto_create_combinations()