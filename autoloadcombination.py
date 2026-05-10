import win32com.client
from win32com.client import CastTo
import sys

def cleanup_test_cases(cases):
    case_col = cases.GetAll()
    to_delete = []
    for i in range(1, case_col.Count + 1):
        rc = case_col.Get(i)
        if rc.Name.startswith("TEST"):
            to_delete.append(rc.Number)
    for num in to_delete:
        cases.Delete(num)
        print(f"Deleted TEST case: {num}")

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
        if rc.Type == 1:  # ข้าม Load Combination
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

    errors = []
    if not dl_nums: errors.append("No Dead Load Cases found")
    if not ll_nums: errors.append("No Live Load Cases found")
    if not wl_nums: errors.append("No Wind Load Cases found")
    if errors:
        print("ERROR:\n" + "\n".join(errors))
        sys.exit()

    print(f"Dead Load  : {len(dl_nums)} Cases {dl_nums}")
    print(f"Live Load  : {len(ll_nums)} Cases {ll_nums}")
    print(f"Wind Load  : {len(wl_nums)} Cases {wl_names}")
    print("-" * 50)

    combo_num = max_num + 1
    print(f"Starting combo from Case: {combo_num}")
    print("-" * 50)
    created = 0

    # === ชุดที่ 1: 1.05DL + 1.27LL + 1.6WL (ULS) ===
    for w in range(len(wl_nums)):
        name_a = f"1.05DL+1.27LL+1.6({wl_names[w]})"
        cases.CreateCombination(combo_num, name_a, 0, 0, 0)
        combo = CastTo(cases.Get(combo_num), "IRobotCaseCombination")
        combo.CombinationType = 0  # ULS
        cf_server = combo.CaseFactors
        for dl in dl_nums:
            cf_server.New(dl, float(1.05))
        for ll in ll_nums:
            cf_server.New(ll, float(1.27))
        cf_server.New(wl_nums[w], float(1.6))
        print(f"Created Combo {combo_num}: {name_a} [ULS]")
        combo_num += 1
        created += 1

    # === ชุดที่ 2: 0.9DL + 1.6WL (ULS) ===
    for w in range(len(wl_nums)):
        name_b = f"0.9DL+1.6({wl_names[w]})"
        cases.CreateCombination(combo_num, name_b, 0, 0, 0)
        combo = CastTo(cases.Get(combo_num), "IRobotCaseCombination")
        combo.CombinationType = 0  # ULS
        cf_server = combo.CaseFactors
        for dl in dl_nums:
            cf_server.New(dl, float(0.9))
        cf_server.New(wl_nums[w], float(1.6))
        print(f"Created Combo {combo_num}: {name_b} [ULS]")
        combo_num += 1
        created += 1

    # === ชุดที่ 3: DL + LL (SLS) ===
    name_sls = "DL+LL"
    cases.CreateCombination(combo_num, name_sls, 0, 0, 0)
    combo = CastTo(cases.Get(combo_num), "IRobotCaseCombination")
    combo.CombinationType = 1  # SLS
    cf_server = combo.CaseFactors
    for dl in dl_nums:
        cf_server.New(dl, float(1.0))
    for ll in ll_nums:
        cf_server.New(ll, float(1.0))
    print(f"Created Combo {combo_num}: {name_sls} [SLS]")
    combo_num += 1
    created += 1

    print("-" * 50)
    print(f"Done! Created {created} Combinations")

if __name__ == "__main__":
    auto_create_combinations()