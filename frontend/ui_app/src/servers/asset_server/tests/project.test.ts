import { assert } from "console";
import Project from  "../project";
import expected from "./project_data.json";

let expectedProjects: any = expected;
let firstProjectId: string = Object.keys(expected)[0];
let firstProject: any = expectedProjects[firstProjectId]

test("create project instance", () => {
    let expectedFirstProject = new Project(firstProject);
    assert(expectedFirstProject.id === firstProject.id)
    assert(expectedFirstProject.is_active === firstProject.is_active)
})