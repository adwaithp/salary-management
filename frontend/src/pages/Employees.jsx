import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getEmployees, createEmployee, updateEmployee, deleteEmployee } from "../api/employees";
import { Plus, Search, Pencil, Trash2, Loader2, X, ChevronLeft, ChevronRight } from "lucide-react";

const DEPARTMENTS = ["engineering","product","design","finance","hr","marketing","operations","sales","legal","data"];
const ROLES = ["employee", "manager", "hr", "admin"];
const EMPTY_FORM = {
  first_name: "", last_name: "", email: "", password: "",
  job_title: "", department: "engineering", country: "",
  salary: "", hire_date: "", role: "employee",
};

function Modal({ title, onClose, children }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={20} />
          </button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
}

function EmployeeForm({ initial, onSubmit, loading, isEdit }) {
  const [form, setForm] = useState(initial);
  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const inputClass = "w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500";
  const labelClass = "block text-xs font-medium text-gray-600 mb-1";

  return (
    <form onSubmit={(e) => { e.preventDefault(); onSubmit(form); }} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>First Name</label>
          <input className={inputClass} value={form.first_name} onChange={set("first_name")} required />
        </div>
        <div>
          <label className={labelClass}>Last Name</label>
          <input className={inputClass} value={form.last_name} onChange={set("last_name")} required />
        </div>
      </div>

      <div>
        <label className={labelClass}>Email</label>
        <input type="email" className={inputClass} value={form.email} onChange={set("email")} required />
      </div>

      {!isEdit && (
        <div>
          <label className={labelClass}>Password</label>
          <input type="password" className={inputClass} value={form.password} onChange={set("password")} required />
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Job Title</label>
          <input className={inputClass} value={form.job_title} onChange={set("job_title")} required />
        </div>
        <div>
          <label className={labelClass}>Country</label>
          <input className={inputClass} value={form.country} onChange={set("country")} required />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Department</label>
          <select className={inputClass} value={form.department} onChange={set("department")}>
            {DEPARTMENTS.map((d) => (
              <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Role</label>
          <select className={inputClass} value={form.role} onChange={set("role")}>
            {ROLES.map((r) => (
              <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Salary (USD)</label>
          <input type="number" className={inputClass} value={form.salary} onChange={set("salary")} required />
        </div>
        <div>
          <label className={labelClass}>Hire Date</label>
          <input type="date" className={inputClass} value={form.hire_date} onChange={set("hire_date")} required />
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <button type="submit" disabled={loading}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
          {loading && <Loader2 size={14} className="animate-spin" />}
          {isEdit ? "Save Changes" : "Add Employee"}
        </button>
      </div>
    </form>
  );
}

export default function Employees() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [modal, setModal] = useState(null); // null | "add" | { type: "edit", employee } | { type: "delete", employee }

  const { data, isLoading } = useQuery({
    queryKey: ["employees", search, page],
    queryFn: () => getEmployees({ search, page }),
  });

  const employees = data?.results ?? data ?? [];
  const totalPages = data?.count ? Math.ceil(data.count / 50) : 1;

  const createMutation = useMutation({
    mutationFn: createEmployee,
    onSuccess: () => { queryClient.invalidateQueries(["employees"]); setModal(null); },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateEmployee(id, data),
    onSuccess: () => { queryClient.invalidateQueries(["employees"]); setModal(null); },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteEmployee,
    onSuccess: () => { queryClient.invalidateQueries(["employees"]); setModal(null); },
  });

  const roleBadge = (role) => {
    const styles = {
      hr: "bg-purple-100 text-purple-700",
      admin: "bg-red-100 text-red-700",
      manager: "bg-blue-100 text-blue-700",
      employee: "bg-gray-100 text-gray-600",
    };
    return (
      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${styles[role] ?? styles.employee}`}>
        {role}
      </span>
    );
  };

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            {data?.count ?? employees.length} total employees
          </p>
        </div>
        <button
          onClick={() => setModal("add")}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          Add Employee
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-4">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          placeholder="Search by name, email or job title..."
          className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={24} className="animate-spin text-blue-500" />
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                {["Name", "Email", "Job Title", "Department", "Country", "Salary", "Role", ""].map((h) => (
                  <th key={h} className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {employees.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{emp.full_name}</td>
                  <td className="px-4 py-3 text-gray-500">{emp.email}</td>
                  <td className="px-4 py-3 text-gray-700">{emp.job_title}</td>
                  <td className="px-4 py-3 text-gray-500 capitalize">{emp.department}</td>
                  <td className="px-4 py-3 text-gray-500">{emp.country}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    ${Number(emp.salary).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">{roleBadge(emp.role)}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2 justify-end">
                      <button
                        onClick={() => setModal({ type: "edit", employee: emp })}
                        className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      >
                        <Pencil size={14} />
                      </button>
                      <button
                        onClick={() => setModal({ type: "delete", employee: emp })}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <p className="text-sm text-gray-500">Page {page} of {totalPages}</p>
          <div className="flex gap-2">
            <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">
              <ChevronLeft size={16} />
            </button>
            <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}
              className="p-2 rounded-lg border border-gray-200 disabled:opacity-40 hover:bg-gray-50">
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Add Modal */}
      {modal === "add" && (
        <Modal title="Add Employee" onClose={() => setModal(null)}>
          <EmployeeForm
            initial={EMPTY_FORM}
            onSubmit={(data) => createMutation.mutate(data)}
            loading={createMutation.isPending}
            isEdit={false}
          />
        </Modal>
      )}

      {/* Edit Modal */}
      {modal?.type === "edit" && (
        <Modal title="Edit Employee" onClose={() => setModal(null)}>
          <EmployeeForm
            initial={{ ...modal.employee, password: "" }}
            onSubmit={(data) => updateMutation.mutate({ id: modal.employee.id, data })}
            loading={updateMutation.isPending}
            isEdit={true}
          />
        </Modal>
      )}

      {/* Delete Confirm */}
      {modal?.type === "delete" && (
        <Modal title="Delete Employee" onClose={() => setModal(null)}>
          <p className="text-gray-600 text-sm mb-6">
            Are you sure you want to remove{" "}
            <span className="font-semibold text-gray-900">{modal.employee.full_name}</span>?
            This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <button onClick={() => setModal(null)}
              className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50">
              Cancel
            </button>
            <button
              onClick={() => deleteMutation.mutate(modal.employee.id)}
              disabled={deleteMutation.isPending}
              className="px-4 py-2 text-sm bg-red-600 hover:bg-red-500 text-white rounded-lg flex items-center gap-2 disabled:opacity-50"
            >
              {deleteMutation.isPending && <Loader2 size={14} className="animate-spin" />}
              Delete
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
