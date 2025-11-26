declare module 'react-cytoscapejs' {
    import { Component } from 'react';
    import cytoscape from 'cytoscape';

    interface CytoscapeComponentProps {
        elements: object[];
        style?: React.CSSProperties;
        stylesheet?: object[];
        layout?: object;
        cy?: (cy: cytoscape.Core) => void;
        className?: string;
    }

    export default class CytoscapeComponent extends Component<CytoscapeComponentProps> { }
}
