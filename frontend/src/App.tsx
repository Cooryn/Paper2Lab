import { Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { DashboardPage } from "./pages/DashboardPage";
import { PaperDetailPage } from "./pages/PaperDetailPage";
import { ReportsPage } from "./pages/ReportsPage";
import { ReproProjectPage } from "./pages/ReproProjectPage";
import { TopicDetailPage } from "./pages/TopicDetailPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/topics/:topicId" element={<TopicDetailPage />} />
        <Route path="/papers/:paperId" element={<PaperDetailPage />} />
        <Route path="/repro-projects/:projectId" element={<ReproProjectPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/reports/:reportId" element={<ReportsPage />} />
      </Routes>
    </Layout>
  );
}

