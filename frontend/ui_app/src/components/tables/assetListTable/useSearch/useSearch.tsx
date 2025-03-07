import { useRef, useState } from "react";

export default function useSearchTerms() {
    const [searchTerms, setSearchTerms] = useState<object>({});
    const searchTermsRef = useRef(searchTerms); // ref fto be used in useColumns calback
    searchTermsRef.current = searchTerms;

    return {searchTermsRef, setSearchTerms}
}