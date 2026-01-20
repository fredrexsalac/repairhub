# BiPSU Repair Hub – Platform Overview

This document explains the goals, behaviors, and operations of the BiPSU Repair Hub portal. It is written for stakeholders who care about the service experience rather than the underlying framework.

---

## 1. Mission

- Provide a reliable booking channel for students who need device repairs handled inside BiPSU study hubs.
- Give volunteer technicians a modern dashboard for triaging requests, communicating decisions, and handing off receipts.
- Maintain safety and policy compliance (e.g., no iPhone battery work, no board-level soldering) through every touchpoint.

---

## 2. Audience Segments

| Segment          | Goals | Key Touchpoints |
|------------------|-------|----------------|
| Students / Clients | Book repair slots, receive SMS/email updates, download receipts | Home page, booking form, status tracker, receipt modal |
| Admin Technicians  | Approve/decline jobs, add notes, monitor parts, lock appointments | Custom admin console with appointments queue, detail pages |
| Repair Coordinators | Monitor throughput, enforce safety rules, analyze earnings summaries | Dashboard metrics, downloadable receipts, appointment logs |

---

## 3. Client Journey

1. **Discover** – Students land on the portal and read service limitations (no soldering, no iPhone battery swaps).
2. **Book** – They select device type, manufacturer, model, preferred schedule, location hub, and payment preference. Dynamic pricing previews show the estimated labor rate immediately.
3. **Confirm** – After acknowledging the booking policies, the request is stored with a tracking ID (e.g., `BIP-260116-DKWT`).
4. **Track** – Students can revisit the `/status` page with their tracking ID or contact number to see latest updates.
5. **Receive** – Once approved or completed, the student can open the receipt modal, see all appointment details, and download a PDF that includes official seals, service breakdown, and a Code128 barcode.

---

## 4. Technician Workflow

1. **Login** – Technicians authenticate at `/admin/login` and reach the appointment queue.
2. **Review** – Each appointment detail view shows issue description, schedule, quoted price, location notes, and safety flags.
3. **Decide** – Status options cover Pending → Approved → In progress → Completed, plus rejection states (parts unavailable, unsupported).
4. **Notes & Parts** – Admin notes capture diagnostics, replacement part orders toggle locking logic, and payments remain tied to the quoted labor matrix.
5. **Receipt Generation** – Clicking “Generate receipt” opens a modal pre-filled with logos, appointment metadata, issue description, total, and barcode, ready for PDF download/printing.

---

## 5. Pricing & Policies

- Labor pricing is predetermined per device type + service. The portal references the service matrix automatically when showing totals, preventing manual errors.
- Hard safety rules:
  - Reject iPhone battery keywords both on the client form and inside admin validators.
  - Block soldering / board-level terms via keyword scans and by removing soldering from the service list entirely.
- Location options are limited to BiPSU-operated study hubs; any special pickup details go into an optional notes field.

---

## 6. Receipts & Compliance

- Receipts always show: appointment ID, client name, device, service, schedule, contact, location, payment method, client program, issue summary, total, technicians’ organization logos, and a thank-you banner.
- Barcodes use the appointment ID for quick reference when students arrive at the hub.
- PDF download relies on the browser’s print-to-PDF workflow so the output can be shared digitally or printed on-site.

---

## 7. Installable Experience (PWA)

- Students can install **“BiPSU Repair – Client”** from supported browsers, pinning the booking portal to their home screen for quick access.
- Technicians can install **“BiPSU Repair – Admin”** for an app-like feel when managing the queue during on-site shifts.
- A shared service worker caches the primary shell (home page, admin panel, CSS, JS, logos) for quicker load times and resilience when campus Wi-Fi drops momentarily.

---

## 8. Data & Security Behaviors

- Each appointment is stored with a masked tracking number for public lookups while keeping detailed notes restricted to admins.
- Session-based auth ensures technicians must explicitly log in and out; logging out clears the session key.
- Contact history is protected via custom messaging threads that only surface to the assigned admin.

---

## 9. Operational Checklists

**Before opening the portal each term:**
- Refresh the service pricing matrix if labor rates changed.
- Review the model suggestion lists to add any new Redmi/Realme/POCO/TECNO phones or laptop series.
- Confirm the policy copy still reflects campus guidelines.

**During daily operations:**
- Monitor the appointment queue at least twice per shift.
- Lock appointments once parts are ordered to avoid conflicting edits.
- Encourage clients to use the receipt download feature so they have a digital copy before leaving the hub.

**At the end of the day:**
- Export or archive receipts for accounting.
- Clear the admin session and verify no pending approvals remain.

---

## 10. Future Enhancements (Conceptual)

- SMS integration for automatic reminders before scheduled drop-offs.
- Technician shift planner to balance workload across hubs.
- Analytics dashboard summarizing approval rates, average turnaround, and most common device issues.

---

### Contact & Ownership

BiPSU Repair Hub is managed by the student-technician organization at Biliran Province State University. Questions or partnership ideas can be directed to the repair coordinators through the admin portal’s contact workflow.

